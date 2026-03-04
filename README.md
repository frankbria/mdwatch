# mdwatch

A live terminal markdown viewer for watching files as they're written. Built with [Textual](https://textual.textualize.io/) for rich TUI rendering.

mdwatch watches a markdown file for changes and incrementally renders new content in the terminal, making it ideal for following along with [showboat](https://github.com/frankbria/showboat) demos or any process that appends to a markdown file over time.

## Relationship to mdr

mdwatch is a companion to [mdr](https://github.com/CleverCloud/mdr), a Rust-based markdown viewer by Clever Cloud. While mdr provides a general-purpose markdown viewer with multiple backends (GUI, webview, TUI) and live reload, mdwatch focuses specifically on **incremental, append-only rendering** in the terminal — optimized for watching demos and logs that grow over time rather than re-rendering the entire document on each change.

## Installation

Requires Python 3.12+.

```bash
# Clone and install with uv
git clone https://github.com/frankbria/mdwatch.git
cd mdwatch
uv sync

# Run directly
uv run mdwatch path/to/file.md

# Or install globally
uv tool install .
mdwatch path/to/file.md
```

## Usage

```bash
# Watch a markdown file (auto-scrolls to new content)
mdwatch demo.md

# Disable auto-follow
mdwatch demo.md --no-follow
```

If the file doesn't exist yet, mdwatch waits for it to be created.

### Keybindings

| Key | Action |
|-----|--------|
| `f` | Toggle follow mode (auto-scroll) |
| `g` | Jump to top |
| `G` | Jump to bottom |
| `o` | Open last image with system viewer |
| `q` | Quit |

### Showboat demo simulation

To see mdwatch in action, run the included simulation script in one terminal while watching in another:

```bash
# Terminal 1
uv run mdwatch /tmp/test-demo.md

# Terminal 2
./scripts/simulate_demo.sh /tmp/test-demo.md
```

## Supported markdown elements

mdwatch parses a subset of markdown tailored for showboat demo output:

- **Headers** (`# H1` through `###### H6`)
- **Timestamps** (italic ISO 8601, e.g. `*2026-03-04T14:30:00Z*`)
- **Paragraphs** (narrative text)
- **Code blocks** (fenced with language tag)
- **Output blocks** (fenced with `` ```output ``)
- **Image references** (`![alt](path)`)
- **Horizontal rules** (`---`)

## Development

```bash
# Install dev dependencies
uv sync

# Run tests
uv run pytest tests/ -v

# Run the app
uv run mdwatch --help
```

## License

[MIT](LICENSE)
