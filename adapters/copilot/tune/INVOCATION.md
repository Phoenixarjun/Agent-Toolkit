# GitHub Copilot: explicit-only Tune invocation

At installation, modify **only the installed user's copy** of `skills/tune/SKILL.md` frontmatter to add:

```yaml
disable-model-invocation: true
```

Do not add this vendor-specific key to Agent Toolkit's canonical skill tree. Confirm the installed Copilot environment recognizes the skill under its explicit invocation and does not auto-trigger it. If this cannot be confirmed, mark explicit-only runtime enforcement `NOT_VERIFIED`; do not promise that a portable instruction alone disables implicit invocation.

The user must separately approve any actual tuning change. Invocation is not blanket write authorization.
