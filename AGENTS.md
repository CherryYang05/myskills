# Agent repository instructions

This is the source repository `CherryYang05/myskills`. The instructions in this file govern repository maintenance. They are not an installable Skill.

## Repository layout

- `skills/external/<name>/SKILL.md`: third-party Skills mirrored from upstream Git repositories. Their exact upstreams and synchronized Git commit SHAs are recorded in `automation/upstreams.json`. Every external Skill directory must have a matching registry entry.
- `skills/personal/<name>/SKILL.md`: self-authored Skills, maintained manually. Never overwrite them during the scheduled upstream sync.
- `automation/scripts/`: trusted synchronization, validation, README / Marketplace generation and guarded PR auto-merge code.
- `automation/tests/`: regression and security tests.
- `.agents/plugins/marketplace.json`: generated plugin catalog for supported ChatGPT workspaces; entries point to `plugins/<name>`.
- `.claude-plugin/marketplace.json`: generated Claude Code plugin catalog.
- `.cursor-plugin/marketplace.json`: generated Cursor marketplace catalog.
- `skills.sh.json`: generated Skills CLI discovery paths pointing at canonical Skills.
- `plugins/<name>/`: generated standalone plugin with root `plugin.json` and a mirrored `skills/<name>/` package, except root-level `.claude-plugin/` and `.cursor-plugin/` installer metadata. Never edit generated packages directly; source Skills retain their full upstream files.
- `README.md`: generated Skill index and installation guidance.
- `UPSTREAM_SYNC_REPORT.md`: generated summary of the most recently prepared and merged upstream sync. See Git history and GitHub Actions to confirm actual completion.
- `docs/architecture.md`: architecture, limitations and two-stage distribution details.

## Safe maintenance workflow

1. Confirm the Git checkout and remote before editing: `git rev-parse --show-toplevel`, `git remote -v` and `git status`. An installed Skills CLI package is not necessarily a source checkout.
2. Inspect the diff before changing or deleting files. Do not commit secrets, credentials, generated Python bytecode or unrelated working-tree changes. Summarize manual deletions and behavioral changes for the user.
3. Preserve every Skill's internal relative paths (references, scripts, assets, metadata). A renamed package or `SKILL.md` name can break clients and existing installations.
4. When adding a third-party Skill, register its true upstream repository, subpath, tracked ref and synchronized full commit SHA in `automation/upstreams.json`. The registry and the `skills/external/` directory set must match exactly.
5. Do not edit generated `README.md`, all three platform marketplace catalogs, `skills.sh.json` or `plugins/` as their source of truth. After Skill or configuration changes, run `python3 automation/scripts/generate.py`. Edit that generator for changes to README prose or catalog layout.
6. Verify results with:
   ```bash
   python3 -m pip install pyyaml
   python3 -m unittest discover -s automation/tests -v
   python3 automation/scripts/verify.py
   python3 automation/scripts/sync.py --check-config
   python3 automation/scripts/generate.py --check
   ```

## Two-stage synchronization safeguards

**Stage 1: upstream → GitHub.** `.github/workflows/sync-upstream.yml` runs Fridays at 12:30 UTC (20:30 Asia/Shanghai). Its candidates may alter only registered `skills/external/` packages, matching generated `plugins/<external-name>/` packages, pinned source SHAs and generated catalogs/configuration. They must pass `Validate Skills` for the exact candidate commit before automatic merge. Do not execute untrusted upstream Skill scripts, bypass CI, overwrite preserved LICENSE / NOTICE files, alter upstream sources inside a candidate, or touch `skills/personal/`.

**Stage 2: GitHub → ChatGPT.** Workspace administrators may import the repository Marketplace and track `master`. The platform's marketplace sync is separate from GitHub Actions. Do not assume a personal ChatGPT account's manually uploaded plugins update automatically; importing or migrating existing plugins needs verification in the target workspace.

For manual installation or updates with the Skills CLI, use `npx skills add CherryYang05/myskills --list` and `npx skills update <skill-name> --global` as appropriate. Verify installed/local changes before overwriting them.

If automation fails, retain the candidate PR and error evidence, inspect the relevant GitHub Actions run and Issue, fix the root cause, and rerun validation. Never report an upstream synchronization as completed solely because an update was detected.
