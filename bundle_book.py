#!/usr/bin/env python3
"""Bundle Mastering Modern DevOps (Second Edition) using technical-book-mcp-server's KDP bundler."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SERVER_ROOT = ROOT.parent / "technical-book-mcp-server"
if SERVER_ROOT.exists():
    sys.path.insert(0, str(SERVER_ROOT))

try:
    import loguru  # noqa: F401
except ModuleNotFoundError:
    import logging
    import types

    _shim = types.ModuleType("loguru")
    _shim.logger = logging.getLogger("book_bundler")
    sys.modules["loguru"] = _shim

from technical_book_mcp_server.utils.book_bundler import (  # noqa: E402
    bundle_book_from_directory,
    render_epub3_package,
    render_standalone_html_book,
)
from technical_book_mcp_server.utils.diagram_renderer import (  # noqa: E402
    generate_cover_svg,
)


def main() -> int:
    result = bundle_book_from_directory(
        ROOT, inside_technicalbook=False, run_pandoc=True
    )
    tb_result = bundle_book_from_directory(
        ROOT, inside_technicalbook=True, run_pandoc=True
    )
    md_text = Path(result["book_md"]).read_text(encoding="utf-8")
    title = "Mastering Modern DevOps (Second Edition)"
    subtitle = (
        "A Comprehensive Guide to Infrastructure, Automation, "
        "Platform Engineering, eBPF, OpenTelemetry, and Cloud-Native Security"
    )
    author = "Christian Chostak"
    for target in (result, tb_result):
        manifest_path = Path(target["kdp_manifest"])
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["bookMetadata"]["title"] = title
        manifest["bookMetadata"]["subtitle"] = subtitle
        manifest["bookMetadata"]["author"] = author
        manifest["bookMetadata"]["edition"] = "Second Edition (v2.0)"
        manifest["bookMetadata"]["technicalDomain"] = "Platform Engineering"
        manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        generate_cover_svg(
            title=title,
            subtitle=subtitle,
            author=author,
            output_path=Path(target["book_html"]).parent / "images" / "cover.svg",
        )
        render_standalone_html_book(
            md_text,
            Path(target["book_html"]),
            title=title,
            subtitle=subtitle,
            author=author,
        )
        render_epub3_package(
            md_text,
            Path(target["book_epub"]),
            title=title,
            subtitle=subtitle,
            author=author,
        )
    print(
        f"Bundled KDP manuscript: {result['book_md']} ({result['book_md_size']} bytes)"
    )
    print(f"HTML5 Book: {result['book_html']}")
    print(f"Kindle EPUB3: {result['book_epub']}")
    print(f"KDP Manifest: {result['kdp_manifest']}")
    print(f"Rendered Diagrams: {result['rendered_diagram_count']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
