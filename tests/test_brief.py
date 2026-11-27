"""通用行为：模型校验、审批标记、排序不改动输入、空简报。"""
from datetime import date

import pytest

from conftest import load_sample_brief
from intel_brief import Item, approve, generate_brief, sort_section


def _item(**overrides):
    fields = {
        "id": "G01",
        "title": "虚构通用条目",
        "publisher": "虚构部门",
        "published_date": date(2026, 11, 3),
        "source_url": "https://example.invalid/g",
        "summary": "虚构摘要。",
        "audience": "虚构对象",
        "conditions": "无",
        "deadline": None,
        "category": "行业动态",
        "approved": True,
        "approved_date": date(2026, 11, 5),
    }
    fields.update(overrides)
    return Item(**fields)


def test_brief_defaults_to_draft():
    brief = load_sample_brief()
    assert brief.status == "draft"
    assert brief.approved_by is None


def test_approve_marks_published_with_approver():
    brief = load_sample_brief()
    approve(brief, "虚构主管")
    assert brief.status == "published"
    assert brief.approved_by == "虚构主管"


def test_approve_with_empty_approver_rejected():
    brief = load_sample_brief()
    with pytest.raises(ValueError):
        approve(brief, "")


def test_summary_over_150_chars_rejected():
    with pytest.raises(ValueError):
        _item(summary="虚" * 151)


def test_summary_exactly_150_chars_accepted():
    assert _item(summary="虚" * 150).summary == "虚" * 150


def test_unknown_category_rejected():
    with pytest.raises(ValueError):
        _item(category="虚构类型")


def test_approved_without_date_rejected():
    with pytest.raises(ValueError):
        _item(approved_date=None)


def test_sort_section_does_not_mutate_input():
    items = [_item(id="A", deadline=date(2026, 12, 1)), _item(id="B", deadline=date(2026, 11, 15))]
    original = list(items)
    ordered = sort_section(items)
    assert [i.id for i in ordered] == ["B", "A"]
    assert items == original


def test_empty_input_gives_empty_brief():
    brief = generate_brief([], "2026-W45", date(2026, 11, 2), date(2026, 11, 8), date(2026, 11, 9))
    assert brief.total_items == 0
    assert brief.excluded == []
