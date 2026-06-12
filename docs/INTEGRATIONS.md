# Agent And Editor Integrations

Codeglance integrations are generated repo-local guidance files. They do not install plugins,
call network APIs, or depend on any agent runtime. Every adapter points the tool back to the same
static artifacts in `.codeglance/outputs`.

## Platform Matrix

| Platform | Files |
| --- | --- |
| Codex | `AGENTS.md`, `.agents/skills/codeglance/SKILL.md` |
| Claude Code | `.claude/skills/codeglance/SKILL.md`, `.claude/commands/codeglance.md` |
| Cursor | `.cursor/rules/codeglance.mdc` |
| Windsurf | `.windsurf/rules/codeglance.md` |
| GitHub Copilot | `.github/copilot-instructions.md` |
| Gemini CLI | `GEMINI.md` |
| Cline | `.clinerules/codeglance.md` |
| Roo Code | `.roo/rules/codeglance.md` |
| Aider | `.aider/codeglance.md` |
| Continue | `.continue/rules/codeglance.md` |

Default install targets are Codex and Claude. Use `--agents all` or `--platform all` for every
supported target.

## Required Context Contract

Every generated guidance file points agents to:

- `.codeglance/outputs/llms.txt`
- `.codeglance/outputs/agent.md`
- `.codeglance/outputs/processes.md`
- `.codeglance/outputs/impact.md`
- `.codeglance/outputs/review.md`
- `.codeglance/outputs/knowledge-graph.toon`

Optional marketplace manifests live under `.codeglance/marketplace/*.json` and include the same
required artifact list plus generate, serve, and ask commands.

## Commands

```bash
codeglance init --agents default
codeglance init --agents all --dry-run --marketplace-manifests
codeglance agents list
codeglance agents plan . --platform codex,cursor --marketplace-manifests
codeglance agents install . --platform cursor --dry-run
codeglance agents validate . --platform all --marketplace-manifests
```

## Safety Rules

- Dry runs write nothing.
- Existing files are conflicts by default.
- `--force` or `--overwrite` is required to replace integration files.
- Generated paths are repo-relative and reject absolute or parent-directory paths.
- Validation reports missing files, modified files, missing required artifact references, unreadable
  files, and invalid marketplace manifests.
