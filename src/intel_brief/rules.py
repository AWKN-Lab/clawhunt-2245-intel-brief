"""收录规则与排序规则（任务原文的机械实现）。

收录（须同时满足，缺一即剔除并记录原因）：
  1. 已审批通过；
  2. 审批日期落在收录窗口（上周一至周日）内；
  3. 有原文链接；
  4. 未过期（无截止日期视为未过期；有截止日期的，截止日期须不早于生成日）；
  5. 未被以往期次收录过。

排序：节内先排有截止日期的条目（截止日期升序），再排无截止日期的条目
（发布日期降序）。分节顺序见 models.SECTION_ORDER。
"""
from __future__ import annotations

from datetime import date

from .models import Item

EXCLUSION_REASONS = {
    "not_approved": "未审批通过",
    "outside_window": "审批日期不在收录窗口内",
    "missing_link": "缺少原文链接",
    "expired": "已过期",
    "already_included": "已被以往期次收录过",
}


def is_eligible(item: Item, week_start: date, week_end: date, as_of: date) -> bool:
    """条目是否可收录。"""
    return eligibility_reason(item, week_start, week_end, as_of) is None


def eligibility_reason(
    item: Item, week_start: date, week_end: date, as_of: date
) -> str | None:
    """返回 None 表示可收录，否则返回剔除原因（任务原文措辞）。"""
    if not item.approved:
        return EXCLUSION_REASONS["not_approved"]
    if item.approved_date is None or not (week_start <= item.approved_date <= week_end):
        return EXCLUSION_REASONS["outside_window"]
    if not item.source_url:
        return EXCLUSION_REASONS["missing_link"]
    if item.deadline is not None and item.deadline < as_of:
        return EXCLUSION_REASONS["expired"]
    if item.already_included:
        return EXCLUSION_REASONS["already_included"]
    return None


def section_sort_key(item: Item) -> tuple:
    """节内排序键：有截止日期的在前（截止日期升序）；无截止日期的在后（发布日期降序）。"""
    if item.deadline is not None:
        return (0, item.deadline, date.min)
    return (1, date.min, _neg_ordinal(item.published_date))


def _neg_ordinal(d: date) -> int:
    return -d.toordinal()


def sort_section(items: list[Item]) -> list[Item]:
    """对同一节内的条目排序，返回新列表（不改动输入）。"""
    return sorted(items, key=section_sort_key)
