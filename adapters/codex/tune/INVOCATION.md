# OpenAI Codex: explicit-only Tune invocation

At installation, copy `openai.yaml` into the installed user's skill directory at:

```text
agents/openai.yaml
```

with the content:

```yaml
policy:
  allow_implicit_invocation: false
```

Do not add this vendor-specific configuration file to Agent Toolkit's canonical skill tree. Confirm the installed Codex environment recognizes the skill under its explicit invocation and does not auto-trigger it. If this cannot be confirmed, mark explicit-only runtime enforcement `NOT_VERIFIED`; do not promise that a portable instruction alone disables implicit invocation.

The user must separately approve any actual tuning change. Invocation is not blanket write authorization.
