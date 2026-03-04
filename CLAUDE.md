# mdwatch

Live terminal markdown viewer for watching showboat demos. Built with Textual.

## Project Structure

```
src/mdwatch/
  app.py        - Textual TUI app, file watcher, click CLI entry point
  parser.py     - Incremental markdown parser (append-only, showboat format)
  widgets.py    - Custom Textual widgets (SegmentHeader, CodeBlock, OutputBlock, etc.)
  __main__.py   - python -m mdwatch entry
tests/
  test_parser.py - 8 parser tests (segment types, incremental parsing, edge cases)
  test_app.py    - 6 app tests (Textual pilot, widget rendering, follow mode)
scripts/
  simulate_demo.sh - Simulates a showboat demo for manual testing
```

## Architecture

- **IncrementalParser** tracks previously-seen text and only returns new segments on each `parse_new()` call. This avoids re-rendering the entire document when the file grows.
- **MdWatchApp** uses `watchfiles` in a background thread (`@work(thread=True)`) to detect file changes, then calls back to the main thread via `call_from_thread`.
- Segments are dataclasses (Header, Paragraph, CodeBlock, OutputBlock, ImageRef, etc.) mapped to Textual widgets via pattern matching.

## Commands

```bash
uv sync                          # Install dependencies
uv run pytest tests/ -v          # Run all tests
uv run mdwatch <file>            # Run the app
uv run mdwatch <file> --no-follow  # Run without auto-scroll
```

## Key Design Decisions

- **Append-only parsing**: The parser assumes content is only appended, never edited. It tracks byte offset to avoid re-parsing.
- **No full markdown support**: Only showboat-relevant elements are parsed (headers, code blocks, output blocks, images, timestamps, paragraphs, horizontal rules).
- **Click for CLI**: Simple argument parsing with `--no-follow` flag.
- **watchfiles over watchdog**: Lighter dependency, works well on Linux/WSL.
