"""Textual app for live markdown demo viewing."""

from __future__ import annotations

import subprocess
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

import click
from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.reactive import reactive
from textual.widgets import Footer, Header, Rule, Static

from mdwatch.parser import (
    CodeBlock,
    Header as MdHeader,
    HorizontalRule,
    ImageRef,
    IncrementalParser,
    OutputBlock,
    Paragraph,
    Segment,
    Timestamp,
)
from mdwatch.widgets import (
    ImagePlaceholder,
    SegmentCodeBlock,
    SegmentHeader,
    SegmentOutputBlock,
    SegmentParagraph,
    SegmentTimestamp,
    StatusBar,
)


def segment_to_widget(segment: Segment) -> Static | Rule:
    """Convert a parsed segment into a Textual widget."""
    match segment:
        case MdHeader(level=level, text=text):
            return SegmentHeader(level, text)
        case Timestamp(text=text):
            return SegmentTimestamp(text)
        case Paragraph(text=text):
            return SegmentParagraph(text)
        case CodeBlock(language=lang, code=code):
            return SegmentCodeBlock(lang, code)
        case OutputBlock(text=text):
            return SegmentOutputBlock(text)
        case ImageRef(alt=alt, path=path):
            return ImagePlaceholder(alt, path)
        case HorizontalRule():
            return Rule()
        case _:
            return Static(str(segment))


class MdWatchApp(App):
    """Live terminal markdown viewer for showboat demos."""

    CSS = """
    #content {
        scrollbar-background: $surface;
        scrollbar-color: $primary;
        padding: 1 2;
    }
    """

    TITLE = "mdwatch"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("f", "toggle_follow", "Follow"),
        Binding("o", "open_image", "Open image"),
        Binding("g", "scroll_home", "Top"),
        Binding("G", "scroll_end", "Bottom"),
        Binding("slash", "search", "Search"),
    ]

    following: reactive[bool] = reactive(True)

    def __init__(self, file_path: str, follow: bool = True) -> None:
        super().__init__()
        self.file_path = Path(file_path).resolve()
        self.following = follow
        self._parser = IncrementalParser()
        self._image_paths: list[str] = []
        self._segment_count = 0
        self._stop_event = threading.Event()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield ScrollableContainer(id="content")
        yield StatusBar()

    def on_mount(self) -> None:
        self.sub_title = self.file_path.name
        status = self.query_one(StatusBar)
        status.file_name = self.file_path.name
        status.following = self.following

        # Initial load
        self._load_file()

        # Start watching
        self._watch_file()

    def _load_file(self) -> None:
        """Read and parse the current file contents."""
        if not self.file_path.exists():
            return
        text = self.file_path.read_text()
        segments = self._parser.parse_new(text)
        self._mount_segments(segments)

    def _mount_segments(self, segments: list[Segment]) -> None:
        """Mount new segment widgets into the content area."""
        if not segments:
            return

        content = self.query_one("#content", ScrollableContainer)
        for segment in segments:
            widget = segment_to_widget(segment)
            content.mount(widget)
            if isinstance(segment, ImageRef):
                # Resolve image path relative to the markdown file
                img_path = self.file_path.parent / segment.path
                self._image_paths.append(str(img_path))

        self._segment_count += len(segments)

        # Update status bar
        status = self.query_one(StatusBar)
        status.segment_count = self._segment_count
        status.last_update = datetime.now(timezone.utc).strftime("%H:%M:%S")

        # Auto-scroll if following
        if self.following:
            self.call_after_refresh(self._scroll_to_end)

    def _scroll_to_end(self) -> None:
        content = self.query_one("#content", ScrollableContainer)
        content.scroll_end(animate=False)

    @work(thread=True)
    def _watch_file(self) -> None:
        """Background thread: watch file for changes via watchfiles."""
        from watchfiles import watch

        for _changes in watch(self.file_path, stop_event=self._stop_event):
            if self._stop_event.is_set():
                break
            self.call_from_thread(self._on_file_changed)

    def on_unmount(self) -> None:
        self._stop_event.set()

    def _on_file_changed(self) -> None:
        """Called from watcher thread when file changes."""
        if not self.file_path.exists():
            return
        text = self.file_path.read_text()
        segments = self._parser.parse_new(text)
        self._mount_segments(segments)

    def action_toggle_follow(self) -> None:
        self.following = not self.following
        status = self.query_one(StatusBar)
        status.following = self.following
        if self.following:
            self._scroll_to_end()

    def action_open_image(self) -> None:
        if self._image_paths:
            path = self._image_paths[-1]
            if Path(path).exists():
                subprocess.Popen(
                    ["xdg-open", path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                self.notify(f"Opening {Path(path).name}")
            else:
                self.notify(f"Image not found: {path}", severity="error")
        else:
            self.notify("No images to open", severity="warning")

    def action_scroll_home(self) -> None:
        self.following = False
        self.query_one(StatusBar).following = False
        content = self.query_one("#content", ScrollableContainer)
        content.scroll_home(animate=False)

    def action_scroll_end(self) -> None:
        self.following = True
        self.query_one(StatusBar).following = True
        self._scroll_to_end()

    def action_search(self) -> None:
        self.notify("Search not yet implemented", severity="information")

    def on_mouse_scroll_down(self) -> None:
        if self.following:
            self.following = False
            self.query_one(StatusBar).following = False

    def on_mouse_scroll_up(self) -> None:
        if self.following:
            self.following = False
            self.query_one(StatusBar).following = False


@click.command()
@click.argument("file", type=click.Path())
@click.option("--no-follow", is_flag=True, help="Don't auto-scroll to new content")
def main(file: str, no_follow: bool) -> None:
    """Watch a markdown file live as it's being written."""
    path = Path(file)
    if not path.exists():
        click.echo(f"Waiting for {file} to be created...", err=True)
        # Wait for the file to appear
        from watchfiles import watch

        parent = path.parent if path.parent.exists() else Path(".")
        for changes in watch(parent):
            if path.exists():
                break

    app = MdWatchApp(file_path=str(path), follow=not no_follow)
    app.run()


if __name__ == "__main__":
    main()
