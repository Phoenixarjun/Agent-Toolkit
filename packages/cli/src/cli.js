import path from 'node:path';
import fs from 'node:fs';
import { loadDistributionIndex, normalizeAdapter, loadContract } from './distribution.js';
import { planInstallation, applyInstallation } from './installer.js';
import { runDoctor } from './doctor.js';
import { startCompanionServer } from './server.js';

function printHelp() {
  console.log(`
Agent Toolkit CLI — Reusable procedures and capabilities for AI coding assistants

Usage:
  agent-toolkit <command> [options]

Commands:
  list [skills|profiles|adapters]      List available toolkit capabilities
  inspect (--skill <id> | --profile <id>) Inspect capability metadata and dependencies
  plan (--skill <id> | --profile <id>) --adapter <target> Preview installation plan (dry-run)
  install (--skill <id> | --profile <id>) --adapter <target> Install into target workspace
  doctor [--into <path>]               Verify installed workspace integrity
  open <career|visualize> [--into <path>] Launch local companion application

Options:
  --skill <id>                         Target standalone skill ID
  --profile <id>                       Target composed profile ID
  --adapter, --agent <target>          Target coding assistant adapter:
                                       claude-code, codex, cursor, gemini-cli,
                                       github-copilot, opencode, antigravity
  --into <dir>                         Target project directory (default: .)
  --all-optional                       Include all optional dependencies
  --force                              Overwrite conflicts (shorthand for --on-conflict replace)
  --on-conflict <abort|replace|keep>   Policy for pre-existing unmanaged files (default: abort)
  --port <number>                      Port for local companion server (default: 4173)
  --json                               Output machine-readable JSON
  --version, -v                        Show package version
  --help, -h                           Show this help message
`);
}

export function parseArgs(args) {
  const parsed = {
    command: null,
    subcommand: null,
    skill: null,
    profile: null,
    adapter: null,
    into: '.',
    allOptional: false,
    force: false,
    onConflict: 'abort',
    port: 4173,
    json: false,
    help: false,
    version: false,
    raw: args,
  };

  let i = 0;
  while (i < args.length) {
    const arg = args[i];
    if (arg === '--help' || arg === '-h') {
      parsed.help = true;
    } else if (arg === '--version' || arg === '-v') {
      parsed.version = true;
    } else if (arg === '--json') {
      parsed.json = true;
    } else if (arg === '--all-optional') {
      parsed.allOptional = true;
    } else if (arg === '--force') {
      parsed.force = true;
      parsed.onConflict = 'replace';
    } else if (arg === '--skill') {
      i++;
      parsed.skill = args[i];
    } else if (arg === '--profile') {
      i++;
      parsed.profile = args[i];
    } else if (arg === '--adapter' || arg === '--agent') {
      i++;
      parsed.adapter = args[i];
    } else if (arg === '--into') {
      i++;
      parsed.into = args[i];
    } else if (arg === '--on-conflict') {
      i++;
      parsed.onConflict = args[i];
    } else if (arg === '--port') {
      i++;
      parsed.port = parseInt(args[i], 10) || 4173;
    } else if (!arg.startsWith('-')) {
      if (!parsed.command) {
        parsed.command = arg;
      } else if (!parsed.subcommand) {
        parsed.subcommand = arg;
      }
    }
    i++;
  }

  return parsed;
}

export async function main(argv = process.argv.slice(2)) {
  const args = parseArgs(argv);
  const index = loadDistributionIndex();

  if (args.version || args.command === 'version') {
    if (args.json) {
      console.log(JSON.stringify({ version: index.packageVersion, commit: index.sourceCommit }));
    } else {
      console.log(index.packageVersion);
    }
    return 0;
  }

  if (args.help || !args.command) {
    printHelp();
    return 0;
  }

  switch (args.command) {
    case 'list': {
      const sub = args.subcommand ? args.subcommand.toLowerCase() : 'all';
      if (args.json) {
        const payload = {};
        if (sub === 'all' || sub === 'skills') payload.skills = index.skills;
        if (sub === 'all' || sub === 'profiles') payload.profiles = index.profiles;
        if (sub === 'all' || sub === 'adapters') payload.adapters = index.adapters;
        console.log(JSON.stringify(payload, null, 2));
      } else {
        if (sub === 'all' || sub === 'skills') {
          console.log('\nAvailable Standalone Skills (16):');
          for (const s of index.skills) {
            console.log(`  - ${s.id.padEnd(22)} (${s.version}) [${s.category}]`);
          }
        }
        if (sub === 'all' || sub === 'profiles') {
          console.log('\nAvailable Composed Profiles (8):');
          for (const p of index.profiles) {
            console.log(`  - ${p.id.padEnd(22)}: ${p.description}`);
          }
        }
        if (sub === 'all' || sub === 'adapters') {
          console.log('\nSupported Assistant Adapters (7):');
          for (const a of index.adapters) {
            console.log(`  - ${a.name.padEnd(16)}: ${a.description}`);
          }
        }
      }
      return 0;
    }

    case 'inspect': {
      if (!args.skill && !args.profile) {
        throw new Error("Must specify capability to inspect with '--skill <id>' or '--profile <id>'.");
      }
      const type = args.profile ? 'profile' : 'skill';
      const id = args.profile || args.skill;

      let meta = null;
      if (type === 'skill') {
        meta = index.skills.find((s) => s.id.toLowerCase() === id.toLowerCase());
      } else {
        meta = index.profiles.find((p) => p.id.toLowerCase() === id.toLowerCase());
      }

      if (!meta) {
        throw new Error(`Capability not found: ${type} '${id}'`);
      }

      if (args.json) {
        console.log(JSON.stringify({ type, capability: meta }, null, 2));
      } else {
        console.log(`\n=== Capability: ${id} (${type}) ===`);
        for (const [k, v] of Object.entries(meta)) {
          console.log(`  ${k}:`, typeof v === 'object' ? JSON.stringify(v) : v);
        }
      }
      return 0;
    }

    case 'plan': {
      if (!args.skill && !args.profile) {
        throw new Error("Must specify capability with '--skill <id>' or '--profile <id>'.");
      }
      if (!args.adapter) {
        throw new Error("Must specify target adapter with '--adapter <name>'. Example: --adapter claude-code");
      }
      const type = args.profile ? 'profile' : 'skill';
      const id = args.profile || args.skill;
      const contract = loadContract(type, id, args.adapter, args.allOptional);
      const plan = planInstallation(args.into, contract, {
        onConflict: args.onConflict,
        force: args.force,
      });

      if (args.json) {
        console.log(JSON.stringify(plan, null, 2));
      } else {
        console.log(`\nInstallation Plan for ${type} '${id}' on ${contract.adapter}:`);
        console.log(`  Target directory: ${plan.targetDir}`);
        console.log(`  Conflict policy:  ${plan.onConflict}`);
        console.log(`  Files to create:  ${plan.filesToCreate.length}`);
        console.log(`  Files to update:  ${plan.filesToUpdate.length}`);
        if (plan.conflicts.length > 0) {
          console.log('\n  Conflicts detected:');
          for (const c of plan.conflicts) {
            console.log(`    - ${c}`);
          }
        }
        if (plan.warnings.length > 0) {
          console.log('\n  Warnings:');
          for (const w of plan.warnings) {
            console.log(`    - ${w}`);
          }
        }
      }
      return plan.conflicts.length > 0 && plan.onConflict === 'abort' ? 1 : 0;
    }

    case 'install': {
      if (!args.skill && !args.profile) {
        throw new Error("Must specify capability with '--skill <id>' or '--profile <id>'.");
      }
      if (!args.adapter) {
        throw new Error("Must specify target adapter with '--adapter <name>'. Example: --adapter claude-code");
      }
      const type = args.profile ? 'profile' : 'skill';
      const id = args.profile || args.skill;
      const contract = loadContract(type, id, args.adapter, args.allOptional);
      const result = applyInstallation(args.into, contract, {
        onConflict: args.onConflict,
        force: args.force,
      });

      if (args.json) {
        console.log(JSON.stringify(result, null, 2));
      } else {
        console.log(`\nSuccessfully installed ${type} '${id}' for ${result.adapter} into ${args.into}:`);
        console.log(`  Files created: ${result.createdFiles.length}`);
        console.log(`  Files updated: ${result.updatedFiles.length}`);
        if (result.backups.length > 0) {
          console.log(`  Backups made:  ${result.backups.length}`);
        }
        if (contract.companionApps && contract.companionApps.length > 0) {
          console.log('\n  Companion applications installed:');
          for (const app of contract.companionApps) {
            console.log(`    - ${app.name}: .agent-toolkit/${app.destination}/ (run 'npx @agent-toolkit-core/cli open ${app.name}')`);
          }
        }
        console.log('\nVerification: Run \'agent-toolkit doctor\' to verify integrity.');
      }
      return 0;
    }

    case 'doctor': {
      const result = runDoctor(args.into);
      if (args.json) {
        console.log(JSON.stringify(result, null, 2));
      } else {
        console.log(`\nAgent Toolkit Doctor: ${result.status}`);
        console.log(`  Target directory: ${result.target_dir}`);
        console.log(`  Manifest present: ${result.manifest_present}`);
        console.log(`  Verified files:   ${result.verified_files}`);
        if (result.missing_files.length > 0) {
          console.log('  Missing files:');
          for (const f of result.missing_files) console.log(`    - ${f}`);
        }
        if (result.corrupted_files.length > 0) {
          console.log('  Corrupted / Modified files:');
          for (const f of result.corrupted_files) console.log(`    - ${f}`);
        }
        if (result.errors.length > 0) {
          console.log('  Errors:');
          for (const e of result.errors) console.log(`    - ${e}`);
        }
      }
      return result.status === 'PASS' ? 0 : 1;
    }

    case 'open': {
      const appName = args.subcommand || args.skill || args.profile;
      if (!appName || !['career', 'visualize'].includes(appName.toLowerCase())) {
        throw new Error("Must specify app to open: 'career' or 'visualize'. Example: agent-toolkit open career");
      }
      const normApp = appName.toLowerCase();
      const appRelPath = path.join(args.into, '.agent-toolkit', 'apps', normApp);
      if (!fs.existsSync(appRelPath)) {
        throw new Error(`Companion app '${normApp}' is not installed in ${args.into}. Install it first with 'agent-toolkit install --skill ${normApp} --adapter <target>'.`);
      }
      const instance = await startCompanionServer(appRelPath, { port: args.port });
      console.log(`\nCompanion Application '${normApp}' is running at:\n  ${instance.url}`);
      console.log('Press Ctrl+C to stop the server.');
      return new Promise(() => {}); // Keep alive until Ctrl+C
    }

    default:
      console.error(`Unknown command: '${args.command}'`);
      printHelp();
      return 1;
  }
}
