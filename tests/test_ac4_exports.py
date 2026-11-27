"""AC4：md 与 pdf 两种格式导出成功（附虚构样例文件）。"""
import shutil
import subprocess

import pytest

from conftest import ROOT, load_sample_brief
from intel_brief import export_md, export_pdf_bytes


def test_md_exports_both_editions():
    brief = load_sample_brief()
    for edition in ("staff", "public"):
        text = export_md(brief, edition)
        assert text.startswith("# 会员空间平台每周情报简报 2026-W45")
        assert "共收录 12 条" in text
        assert "补贴申报（3 条）" in text
        assert "关于申报 2026 年度虚构产业扶持补贴的通知" in text


def test_pdf_exports_both_editions_are_valid_pdfs():
    brief = load_sample_brief()
    for edition in ("staff", "public"):
        data = export_pdf_bytes(brief, edition)
        assert data.startswith(b"%PDF-")
        assert data.rstrip().endswith(b"%%EOF")
        assert len(data) > 1000, edition


def test_pdf_has_at_least_one_page():
    if shutil.which("pdfinfo") is None:
        pytest.skip("本机无 pdfinfo，跳过页数核对")
    brief = load_sample_brief()
    out = subprocess.run(
        ["pdfinfo", "-"], input=export_pdf_bytes(brief, "staff"),
        capture_output=True, timeout=60,
    ).stdout.decode("utf-8", errors="replace")
    pages = [ln for ln in out.splitlines() if ln.startswith("Pages:")]
    assert pages and int(pages[0].split(":")[1].strip()) >= 1


def test_pdf_text_contains_issue_and_sections():
    if shutil.which("pdftotext") is None:
        pytest.skip("本机无 pdftotext，跳过 PDF 文本提取核对")
    brief = load_sample_brief()
    text = subprocess.run(
        ["pdftotext", "-", "-"], input=export_pdf_bytes(brief, "staff"),
        capture_output=True, timeout=60,
    ).stdout.decode("utf-8", errors="replace")
    assert "2026-W45" in text
    for section in ("补贴申报", "资质认定", "税收优惠", "行业动态", "活动通知"):
        assert section in text, section


def test_pdf_export_is_deterministic():
    """同一次简报两次导出须字节一致，否则 MANIFEST 无法自证。"""
    brief = load_sample_brief()
    for edition in ("staff", "public"):
        assert export_pdf_bytes(brief, edition) == export_pdf_bytes(brief, edition)


def test_unknown_edition_rejected():
    brief = load_sample_brief()
    with pytest.raises(ValueError):
        export_md(brief, "internal")
    with pytest.raises(ValueError):
        export_pdf_bytes(brief, "internal")


def test_sample_files_exist_in_examples():
    expected = [
        "brief-2026-W45-staff.md",
        "brief-2026-W45-public.md",
        "brief-2026-W45-staff.pdf",
        "brief-2026-W45-public.pdf",
    ]
    for name in expected:
        path = ROOT / "examples" / name
        assert path.is_file(), name
        assert path.stat().st_size > 0, name
