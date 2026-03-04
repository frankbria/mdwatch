"""Custom Textual widgets for rendering showboat markdown segments."""

from __future__ import annotations

from datetime import datetime, timezone

from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from textual.reactive import reactive
from textual.widgets import Static, Rule


class SegmentHeader(Static):
    """Renders a markdown header with level-based styling."""

    DEFAULT_CSS = """
    SegmentHeader {
        margin: 1 0 0 0;
        color: $accent;
        text-style: bold;
    }
    """

    def __init__(self, level: int, text: str) -> None:
        prefix = "#" * level
        markup = Text(f"{prefix} {text}", style="bold")
        if level == 1:
            markup.stylize("underline")
        elif level >= 3:
            markup.stylize("dim")
        super().__init__(markup)


class SegmentTimestamp(Static):
    """Renders an ISO timestamp in dim italic style."""

    DEFAULT_CSS = """
    SegmentTimestamp {
        color: $text-muted;
        text-style: italic;
        margin: 0 0 1 0;
    }
    """


class SegmentParagraph(Static):
    """Renders a plain text paragraph."""

    DEFAULT_CSS = """
    SegmentParagraph {
        margin: 0 0 1 0;
    }
    """


class SegmentCodeBlock(Static):
    """Renders a fenced code block with syntax highlighting."""

    DEFAULT_CSS = """
    SegmentCodeBlock {
        margin: 0 1 1 1;
        padding: 0;
    }
    """

    def __init__(self, language: str, code: str) -> None:
        lang_label = Text(f" {language} ", style="bold on #333333")
        syntax = Syntax(
            code,
            lexer=language if language != "text" else "text",
            theme="monokai",
            line_numbers=False,
            word_wrap=True,
        )
        panel = Panel(
            syntax,
            title=lang_label,
            title_align="left",
            border_style="bright_blue",
            padding=(0, 1),
        )
        super().__init__(panel)


class SegmentOutputBlock(Static):
    """Renders a captured output block with distinct styling."""

    DEFAULT_CSS = """
    SegmentOutputBlock {
        margin: 0 1 1 1;
        padding: 0;
    }
    """

    def __init__(self, text: str) -> None:
        content = Text(text, style="")
        panel = Panel(
            content,
            title=Text(" output ", style="bold on #1a3a1a"),
            title_align="left",
            border_style="green",
            padding=(0, 1),
        )
        super().__init__(panel)


class ImagePlaceholder(Static):
    """Renders a placeholder for an image with its path."""

    DEFAULT_CSS = """
    ImagePlaceholder {
        margin: 0 1 1 1;
        padding: 0;
    }
    """

    def __init__(self, alt: str, path: str) -> None:
        from rich.box import SIMPLE_HEAVY

        self.image_path = path
        label = alt or "image"
        content = Text.assemble(
            ("  ", ""),
            (f" {label} ", "bold"),
            ("\n", ""),
            ("  ", ""),
            (f" {path}", "dim italic"),
            ("\n", ""),
            ("  ", ""),
            (" [o] open in viewer ", "dim"),
        )
        panel = Panel(
            content,
            box=SIMPLE_HEAVY,
            border_style="bright_magenta",
            padding=(0, 1),
        )
        super().__init__(panel)


class StatusBar(Static):
    """Bottom status bar showing file info and follow state."""

    DEFAULT_CSS = """
    StatusBar {
        dock: bottom;
        height: 1;
        background: $primary;
        color: $text;
        padding: 0 1;
    }
    """

    file_name: reactive[str] = reactive("")
    following: reactive[bool] = reactive(True)
    segment_count: reactive[int] = reactive(0)
    last_update: reactive[str] = reactive("")

    def render(self) -> Text:
        parts = []

        # Follow indicator
        if self.following:
            parts.append((" LIVE ", "bold white on green"))
        else:
            parts.append((" PAUSED ", "bold white on red"))

        parts.append(("  ", ""))
        parts.append((self.file_name, "bold"))
        parts.append(("  ", ""))
        parts.append((f"{self.segment_count} blocks", "dim"))

        if self.last_update:
            parts.append(("  ", ""))
            parts.append((f"updated {self.last_update}", "dim italic"))

        parts.append(("  ", ""))
        parts.append(("f:follow  o:open  /:search  q:quit", "dim"))

        return Text.assemble(*parts)
