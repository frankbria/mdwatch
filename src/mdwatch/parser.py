"""Parse showboat-format markdown into typed segments for incremental rendering.

Showboat demo files are append-only: content is added via `showboat note`,
`showboat exec`, and `showboat image` commands. This parser exploits that
property to enable incremental parsing — only new bytes are parsed on each
file change, and incomplete segments (e.g., unclosed fences) are held back
until they're complete.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


# --- Segment types ---


@dataclass(frozen=True)
class Header:
    level: int
    text: str


@dataclass(frozen=True)
class Timestamp:
    text: str


@dataclass(frozen=True)
class Paragraph:
    text: str


@dataclass(frozen=True)
class CodeBlock:
    language: str
    code: str


@dataclass(frozen=True)
class OutputBlock:
    text: str


@dataclass(frozen=True)
class ImageRef:
    alt: str
    path: str


@dataclass(frozen=True)
class HorizontalRule:
    pass


Segment = Header | Timestamp | Paragraph | CodeBlock | OutputBlock | ImageRef | HorizontalRule

# --- Patterns ---

_FENCE_OPEN = re.compile(r"^```(\w*)\s*$")
_FENCE_CLOSE = re.compile(r"^```\s*$")
_HEADER = re.compile(r"^(#{1,6})\s+(.+)$")
_IMAGE = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$")
_TIMESTAMP = re.compile(r"^\*(\d{4}-\d{2}-\d{2}T[\d:.]+Z?)\*\s*$")
_HR = re.compile(r"^---+\s*$")


def parse_segments(text: str) -> list[Segment]:
    """Parse full markdown text into a list of segments."""
    segments: list[Segment] = []
    lines = text.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]

        # Blank lines — skip
        if not line.strip():
            i += 1
            continue

        # Fenced code block
        fence_match = _FENCE_OPEN.match(line)
        if fence_match:
            lang = fence_match.group(1)
            code_lines: list[str] = []
            i += 1
            closed = False
            while i < len(lines):
                if _FENCE_CLOSE.match(lines[i]):
                    closed = True
                    i += 1
                    break
                code_lines.append(lines[i])
                i += 1
            if not closed:
                break  # Incomplete fence — stop parsing here
            code = "\n".join(code_lines)
            if lang == "output":
                segments.append(OutputBlock(text=code))
            else:
                segments.append(CodeBlock(language=lang or "text", code=code))
            continue

        # Header
        header_match = _HEADER.match(line)
        if header_match:
            segments.append(Header(level=len(header_match.group(1)), text=header_match.group(2)))
            i += 1
            continue

        # Timestamp
        ts_match = _TIMESTAMP.match(line)
        if ts_match:
            segments.append(Timestamp(text=ts_match.group(1)))
            i += 1
            continue

        # Image reference
        img_match = _IMAGE.match(line)
        if img_match:
            segments.append(ImageRef(alt=img_match.group(1), path=img_match.group(2)))
            i += 1
            continue

        # Horizontal rule
        if _HR.match(line):
            segments.append(HorizontalRule())
            i += 1
            continue

        # Paragraph — collect contiguous non-blank, non-special lines
        para_lines: list[str] = []
        while i < len(lines):
            ln = lines[i]
            if not ln.strip():
                break
            if _FENCE_OPEN.match(ln) or _HEADER.match(ln) or _IMAGE.match(ln) or _TIMESTAMP.match(ln) or _HR.match(ln):
                break
            para_lines.append(ln)
            i += 1
        if para_lines:
            segments.append(Paragraph(text="\n".join(para_lines)))

    return segments


@dataclass
class IncrementalParser:
    """Tracks parse state across file changes for incremental rendering.

    Only parses new content appended since the last call. Holds back
    incomplete segments (unclosed fences) until the next update.
    """

    _last_offset: int = 0
    _pending_tail: str = ""

    def parse_new(self, full_text: str) -> list[Segment]:
        """Parse only newly appended content, returning new complete segments.

        The caller should render these segments and append them to the display.
        Previously returned segments are never re-returned.
        """
        if len(full_text) <= self._last_offset and not self._pending_tail:
            return []

        # Combine any previously pending (incomplete) text with new content
        new_content = self._pending_tail + full_text[self._last_offset :]
        segments = parse_segments(new_content)

        # Check if there's an incomplete segment at the end by trying to
        # re-parse — if the last segment changes when we add more text,
        # we know it was incomplete. Instead, we use a simpler heuristic:
        # check if the text ends mid-fence.
        remaining = new_content
        if segments:
            # Reconstruct what was successfully parsed to find the boundary
            parsed_end = self._find_parsed_boundary(new_content, segments)
            self._pending_tail = new_content[parsed_end:]
        else:
            self._pending_tail = new_content

        self._last_offset = len(full_text)
        return segments

    def _find_parsed_boundary(self, text: str, segments: list[Segment]) -> int:
        """Find where in `text` the successfully parsed segments end.

        We re-scan the text line by line, matching against parsed segments,
        to determine the byte boundary of fully parsed content.
        """
        lines = text.split("\n")
        i = 0
        seg_idx = 0

        while i < len(lines) and seg_idx < len(segments):
            line = lines[i]

            if not line.strip():
                i += 1
                continue

            seg = segments[seg_idx]

            if isinstance(seg, (CodeBlock, OutputBlock)):
                # Skip opening fence + content + closing fence
                i += 1  # opening fence
                code_lines = seg.text.split("\n") if isinstance(seg, OutputBlock) else seg.code.split("\n")
                i += len(code_lines)
                i += 1  # closing fence
                seg_idx += 1
            elif isinstance(seg, Paragraph):
                para_lines = seg.text.split("\n")
                i += len(para_lines)
                seg_idx += 1
            else:
                # Single-line segments
                i += 1
                seg_idx += 1

        # Convert line index back to character offset
        offset = 0
        for line_idx in range(min(i, len(lines))):
            offset += len(lines[line_idx]) + 1  # +1 for newline

        return min(offset, len(text))

    def reset(self) -> None:
        """Reset parser state for a full re-parse."""
        self._last_offset = 0
        self._pending_tail = ""
