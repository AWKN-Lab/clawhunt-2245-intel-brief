"""AC2：对外版中不出现任何会员企业名称（有测试）。"""
import shutil
import subprocess

import pytest

from conftest import MEMBER_NAMES, load_sample_brief
from intel_brief import export_md, export_pdf_bytes


def test_public_md_contains_no_member_name():
    brief = load_sample_brief()
    public = export_md(brief, "public")
    for name in MEMBER_NAMES:
        assert name not in public, name


def test_public_md_has_no_related_members_line():
    brief = load_sample_brief()
    public = export_md(brief, "public")
    assert "可能相关的会员" not in public
    assert "会员企业" not in public


def test_staff_md_contains_member_names():
    brief = load_sample_brief()
    staff = export_md(brief, "staff")
    for name in MEMBER_NAMES:
        assert name in staff, name


def test_staff_md_has_related_members_lines():
    brief = load_sample_brief()
    staff = export_md(brief, "staff")
    assert staff.count("可能相关的会员") == 5


def test_public_pdf_text_contains_no_member_name():
    if shutil.which("pdftotext") is None:
        pytest.skip("本机无 pdftotext，跳过 PDF 文本提取核对")
    brief = load_sample_brief()
    pdf_bytes = export_pdf_bytes(brief, "public")
    text = subprocess.run(
        ["pdftotext", "-", "-"], input=pdf_bytes, capture_output=True, timeout=60
    ).stdout.decode("utf-8", errors="replace")
    for name in MEMBER_NAMES:
        assert name not in text, name


def test_staff_pdf_text_contains_member_names():
    if shutil.which("pdftotext") is None:
        pytest.skip("本机无 pdftotext，跳过 PDF 文本提取核对")
    brief = load_sample_brief()
    pdf_bytes = export_pdf_bytes(brief, "staff")
    text = subprocess.run(
        ["pdftotext", "-", "-"], input=pdf_bytes, capture_output=True, timeout=60
    ).stdout.decode("utf-8", errors="replace")
    for name in MEMBER_NAMES:
        assert name in text, name
