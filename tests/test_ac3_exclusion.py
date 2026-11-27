"""AC3：已过期或缺少原文链接的条目未被收录（有测试）。"""
from datetime import date

from conftest import load_sample_brief
from intel_brief import Item, eligibility_reason, is_eligible

WEEK_START = date(2026, 11, 2)
WEEK_END = date(2026, 11, 8)
AS_OF = date(2026, 11, 9)


def _base_item(**overrides):
    fields = {
        "id": "T01",
        "title": "虚构测试条目",
        "publisher": "虚构部门",
        "published_date": date(2026, 11, 3),
        "source_url": "https://example.invalid/test",
        "summary": "虚构摘要。",
        "audience": "虚构对象",
        "conditions": "无",
        "deadline": None,
        "category": "行业动态",
        "approved": True,
        "approved_date": date(2026, 11, 5),
        "already_included": False,
    }
    fields.update(overrides)
    return Item(**fields)


def test_five_ineligible_items_excluded_with_reasons():
    brief = load_sample_brief()
    reasons = {item.id: reason for item, reason in brief.excluded}
    assert reasons == {
        "X01": "已过期",
        "X02": "缺少原文链接",
        "X03": "已被以往期次收录过",
        "X04": "未审批通过",
        "X05": "审批日期不在收录窗口内",
    }


def test_excluded_ids_absent_from_all_sections():
    brief = load_sample_brief()
    included = {i.id for items in brief.sections.values() for i in items}
    assert included.isdisjoint({"X01", "X02", "X03", "X04", "X05"})


def test_expired_item_rejected():
    assert eligibility_reason(
        _base_item(deadline=date(2026, 11, 1)), WEEK_START, WEEK_END, AS_OF
    ) == "已过期"


def test_deadline_on_generation_day_not_expired():
    assert is_eligible(_base_item(deadline=AS_OF), WEEK_START, WEEK_END, AS_OF)


def test_missing_link_rejected():
    assert eligibility_reason(
        _base_item(source_url=None), WEEK_START, WEEK_END, AS_OF
    ) == "缺少原文链接"


def test_empty_link_rejected():
    assert eligibility_reason(
        _base_item(source_url=""), WEEK_START, WEEK_END, AS_OF
    ) == "缺少原文链接"


def test_already_included_rejected():
    assert eligibility_reason(
        _base_item(already_included=True), WEEK_START, WEEK_END, AS_OF
    ) == "已被以往期次收录过"


def test_not_approved_rejected():
    assert eligibility_reason(
        _base_item(approved=False, approved_date=None), WEEK_START, WEEK_END, AS_OF
    ) == "未审批通过"


def test_approved_outside_window_rejected():
    assert eligibility_reason(
        _base_item(approved_date=date(2026, 10, 30)), WEEK_START, WEEK_END, AS_OF
    ) == "审批日期不在收录窗口内"


def test_approved_on_window_edges_accepted():
    assert is_eligible(_base_item(approved_date=WEEK_START), WEEK_START, WEEK_END, AS_OF)
    assert is_eligible(_base_item(approved_date=WEEK_END), WEEK_START, WEEK_END, AS_OF)


def test_fully_eligible_item_accepted():
    assert eligibility_reason(_base_item(), WEEK_START, WEEK_END, AS_OF) is None
