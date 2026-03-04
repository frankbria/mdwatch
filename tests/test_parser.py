"""Tests for the showboat markdown segment parser."""

from mdwatch.parser import (
    CodeBlock,
    Header,
    HorizontalRule,
    ImageRef,
    IncrementalParser,
    OutputBlock,
    Paragraph,
    Timestamp,
    parse_segments,
)

SAMPLE_SHOWBOAT = """\
# Setting Up a Python Project

*2026-02-06T15:30:00Z*

First, let's create a virtual environment.

```bash
python3 -m venv .venv && echo 'Done'
```

```output
Done
```

Now let's verify it works.

```python3
print('Hello from Python')
```

```output
Hello from Python
```

---

```bash
agent-browser screenshot feature.png && echo feature.png
```

![feature](feature.png)
"""


def test_parse_full_showboat_doc():
    segments = parse_segments(SAMPLE_SHOWBOAT)
    assert segments[0] == Header(level=1, text="Setting Up a Python Project")
    assert segments[1] == Timestamp(text="2026-02-06T15:30:00Z")
    assert segments[2] == Paragraph(text="First, let's create a virtual environment.")
    assert segments[3] == CodeBlock(language="bash", code="python3 -m venv .venv && echo 'Done'")
    assert segments[4] == OutputBlock(text="Done")
    assert segments[5] == Paragraph(text="Now let's verify it works.")
    assert segments[6] == CodeBlock(language="python3", code="print('Hello from Python')")
    assert segments[7] == OutputBlock(text="Hello from Python")
    assert segments[8] == HorizontalRule()
    assert segments[9] == CodeBlock(
        language="bash", code="agent-browser screenshot feature.png && echo feature.png"
    )
    assert segments[10] == ImageRef(alt="feature", path="feature.png")
    assert len(segments) == 11


def test_parse_incomplete_fence():
    """Unclosed code fence should not produce a segment."""
    text = "# Title\n\n```bash\necho hello\n"
    segments = parse_segments(text)
    assert len(segments) == 1
    assert segments[0] == Header(level=1, text="Title")


def test_parse_empty():
    assert parse_segments("") == []
    assert parse_segments("\n\n\n") == []


def test_incremental_parser_basic():
    parser = IncrementalParser()

    # First chunk: header + timestamp
    text1 = "# Demo\n\n*2026-03-04T10:00:00Z*\n"
    segs1 = parser.parse_new(text1)
    assert len(segs1) == 2
    assert segs1[0] == Header(level=1, text="Demo")
    assert segs1[1] == Timestamp(text="2026-03-04T10:00:00Z")

    # Second chunk: add a paragraph
    text2 = text1 + "\nHello world.\n"
    segs2 = parser.parse_new(text2)
    assert len(segs2) == 1
    assert segs2[0] == Paragraph(text="Hello world.")

    # Third chunk: add a code block
    text3 = text2 + "\n```bash\nls -la\n```\n"
    segs3 = parser.parse_new(text3)
    assert len(segs3) == 1
    assert segs3[0] == CodeBlock(language="bash", code="ls -la")


def test_incremental_parser_partial_write():
    """Mid-write of a code block should be held back until complete."""
    parser = IncrementalParser()

    # Write header
    text1 = "# Demo\n"
    segs1 = parser.parse_new(text1)
    assert len(segs1) == 1

    # Partial code block (no closing fence)
    text2 = text1 + "\n```bash\necho hello\n"
    segs2 = parser.parse_new(text2)
    assert len(segs2) == 0  # held back

    # Complete the code block
    text3 = text2 + "```\n"
    segs3 = parser.parse_new(text3)
    assert len(segs3) == 1
    assert segs3[0] == CodeBlock(language="bash", code="echo hello")


def test_incremental_no_change():
    parser = IncrementalParser()
    text = "# Title\n"
    parser.parse_new(text)
    assert parser.parse_new(text) == []


def test_image_ref():
    segments = parse_segments("![screenshot](app.png)\n")
    assert segments == [ImageRef(alt="screenshot", path="app.png")]


def test_multiline_paragraph():
    text = "This is line one.\nThis continues on line two.\n"
    segments = parse_segments(text)
    assert segments == [Paragraph(text="This is line one.\nThis continues on line two.")]
