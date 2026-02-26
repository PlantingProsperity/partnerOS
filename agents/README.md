# Agents Directory

This directory controls agent hot-loading.

- `agents/roster/`: Bench (templates and inactive agents)
- `agents/active/`: Floor (currently running agents)
- `agents/archive/`: Exit interview (deprecated agents)

Hot-loading rule:
- Hire: move a markdown file from `agents/roster/` to `agents/active/`.
- Fire: move a markdown file from `agents/active/` to `agents/archive/`.

Notes:
- The System Watcher should detect changes and load/unload contexts.
- Keep one agent per file.
