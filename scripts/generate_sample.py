"""生成虚构样例简报（两种版本 × 两种格式）到 examples/。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

from conftest import load_sample_items  # noqa: E402
from intel_brief import export_md, export_pdf_bytes, generate_brief  # noqa: E402
from datetime import date  # noqa: E402


def main() -> int:
    data, items = load_sample_items()
    brief = generate_brief(
        items,
        data["issue_no"],
        date.fromisoformat(data["week_start"]),
        date.fromisoformat(data["week_end"]),
        date.fromisoformat(data["as_of"]),
    )
    examples = ROOT / "examples"
    examples.mkdir(exist_ok=True)
    for edition in ("staff", "public"):
        md_path = examples / ("brief-%s-%s.md" % (data["issue_no"], edition))
        pdf_path = examples / ("brief-%s-%s.pdf" % (data["issue_no"], edition))
        md_path.write_text(export_md(brief, edition), encoding="utf-8")
        pdf_path.write_bytes(export_pdf_bytes(brief, edition))
        print("wrote %s (%d bytes)" % (md_path.name, md_path.stat().st_size))
        print("wrote %s (%d bytes)" % (pdf_path.name, pdf_path.stat().st_size))
    print("brief %s: %d items included, %d excluded" % (brief.issue_no, brief.total_items, len(brief.excluded)))
    for item, reason in brief.excluded:
        print("excluded %s: %s" % (item.id, reason))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
