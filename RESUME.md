# Resume Prompt

Copy everything below and paste it when starting a new Claude session in `/home/frankbria/projects/mdwatch`:

---

## Context

I just built `mdwatch` — a live terminal markdown viewer for watching showboat demos. The code is complete and all 14 tests pass. I need to:

1. **Initialize a git repo, create the GitHub remote, and push the initial commit**
2. **Verify the app works interactively** by running the simulation script

## What's done

- `pyproject.toml` — uv-managed Python project, hatchling build
- `src/mdwatch/parser.py` — Incremental showboat markdown parser (8 tests passing)
- `src/mdwatch/app.py` — Textual TUI app with file watcher, follow mode, keybindings
- `src/mdwatch/widgets.py` — Custom widgets: SegmentHeader, CodeBlock, OutputBlock, ImagePlaceholder, StatusBar
- `src/mdwatch/__main__.py` — `python -m mdwatch` entry
- `src/mdwatch/__init__.py` — package init
- `tests/test_parser.py` — 8 parser tests
- `tests/test_app.py` — 6 app tests (Textual pilot)
- `scripts/simulate_demo.sh` — Demo simulation script
- `.gitignore` — Python/IDE/OS ignores
- Tool is installed globally: `mdwatch --help` works

Also updated `mdr` (separate repo at `/home/frankbria/projects/mdr/`):
- Added `--follow` / `-f` flag for auto-scroll on file changes
- Fixed WSL auto-detection (was picking egui, now picks tui)
- Binary rebuilt and installed at `~/.cargo/bin/mdr`

## What to do now

```bash
# 1. Init git and make initial commit
git init && git branch -m main
git add pyproject.toml src/ tests/ scripts/ .gitignore README.md uv.lock
git commit -m "Initial commit: mdwatch live terminal markdown viewer"

# 2. Create GitHub repo and push
gh repo create frankbria/mdwatch --public --source=. --push

# 3. Run tests to confirm everything works
uv sync && uv run pytest tests/ -v

# 4. Interactive test (run in two terminals):
# Terminal 1: mdwatch /tmp/test-demo.md
# Terminal 2: ./scripts/simulate_demo.sh /tmp/test-demo.md
```

## Plan file
The full implementation plan is at `~/.claude/plans/playful-purring-candle.md`

## mdr changes (separate repo)
The mdr changes at `/home/frankbria/projects/mdr/` are uncommitted — they should be committed separately when ready. Changes: `src/main.rs` (--follow flag, WSL detection) and `src/backend/tui.rs` (follow mode logic).
