"""Smoke tests for the MdWatchApp using Textual's pilot."""

import asyncio
import tempfile
from pathlib import Path

import pytest
from textual.widgets import Static

from mdwatch.app import MdWatchApp
from mdwatch.widgets import (
    ImagePlaceholder,
    SegmentCodeBlock,
    SegmentHeader,
    SegmentOutputBlock,
    SegmentParagraph,
    SegmentTimestamp,
    StatusBar,
)


@pytest.fixture
def demo_file(tmp_path):
    f = tmp_path / "demo.md"
    f.write_text("# Test Demo\n\n*2026-03-04T10:00:00Z*\n")
    return f


@pytest.mark.asyncio
async def test_app_loads_initial_content(demo_file):
    """App should render existing file content on mount."""
    app = MdWatchApp(file_path=str(demo_file))
    async with app.run_test() as pilot:
        await pilot.pause()
        headers = app.query(SegmentHeader)
        assert len(headers) == 1
        timestamps = app.query(SegmentTimestamp)
        assert len(timestamps) == 1


@pytest.mark.asyncio
async def test_on_file_changed_directly(demo_file):
    """Calling _on_file_changed directly should render new segments."""
    app = MdWatchApp(file_path=str(demo_file))
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.pause()

        # Append content and trigger the handler directly (bypasses inotify)
        with open(demo_file, "a") as f:
            f.write("\nHello from the test.\n")

        app._on_file_changed()
        await pilot.pause()

        paragraphs = app.query(SegmentParagraph)
        assert len(paragraphs) >= 1


@pytest.mark.asyncio
async def test_follow_mode_toggle(demo_file):
    """Pressing 'f' should toggle follow mode."""
    app = MdWatchApp(file_path=str(demo_file))
    async with app.run_test() as pilot:
        await pilot.pause()

        status = app.query_one(StatusBar)
        assert status.following is True

        await pilot.press("f")
        await pilot.pause()
        assert status.following is False

        await pilot.press("f")
        await pilot.pause()
        assert status.following is True


@pytest.mark.asyncio
async def test_code_block_rendering(tmp_path):
    """Code blocks should render as SegmentCodeBlock widgets."""
    f = tmp_path / "demo.md"
    f.write_text("# Demo\n\n```python\nprint('hello')\n```\n")

    app = MdWatchApp(file_path=str(f))
    async with app.run_test() as pilot:
        await pilot.pause()
        code_blocks = app.query(SegmentCodeBlock)
        assert len(code_blocks) == 1


@pytest.mark.asyncio
async def test_output_block_rendering(tmp_path):
    """Output blocks should render as SegmentOutputBlock widgets."""
    f = tmp_path / "demo.md"
    f.write_text("# Demo\n\n```output\nhello\n```\n")

    app = MdWatchApp(file_path=str(f))
    async with app.run_test() as pilot:
        await pilot.pause()
        output_blocks = app.query(SegmentOutputBlock)
        assert len(output_blocks) == 1


@pytest.mark.asyncio
async def test_image_placeholder(tmp_path):
    """Image refs should render as ImagePlaceholder widgets."""
    f = tmp_path / "demo.md"
    f.write_text("# Demo\n\n![screenshot](app.png)\n")

    app = MdWatchApp(file_path=str(f))
    async with app.run_test() as pilot:
        await pilot.pause()
        placeholders = app.query(ImagePlaceholder)
        assert len(placeholders) == 1
        assert placeholders[0].image_path == "app.png"
