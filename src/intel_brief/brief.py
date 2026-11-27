"""简报生成：分节、排序、剔除留痕、审批标记。"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from .models import SECTION_ORDER, Item
from .rules import eligibility_reason, sort_section


@dataclass
class Brief:
    """一期简报草稿。status 为 draft 时尚未主管审批；审批后为 published。"""

    issue_no: str
    week_start: date
    week_end: date
    generated_at: date
    sections: dict[str, list[Item]] = field(default_factory=dict)
    excluded: list[tuple[Item, str]] = field(default_factory=list)
    status: str = "draft"
    approved_by: str | None = None

    @property
    def total_items(self) -> int:
        return sum(len(v) for v in self.sections.values())


def generate_brief(
    items: list[Item],
    issue_no: str,
    week_start: date,
    week_end: date,
    as_of: date,
) -> Brief:
    """生成一期简报：收录符合规则的条目分节排序；剔除的条目逐条记录原因。"""
    brief = Brief(
        issue_no=issue_no,
        week_start=week_start,
        week_end=week_end,
        generated_at=as_of,
    )
    grouped: dict[str, list[Item]] = {section: [] for section in SECTION_ORDER}
    for item in items:
        reason = eligibility_reason(item, week_start, week_end, as_of)
        if reason is None:
            grouped[item.category].append(item)
        else:
            brief.excluded.append((item, reason))
    for section in SECTION_ORDER:
        brief.sections[section] = sort_section(grouped[section])
    return brief


def approve(brief: Brief, approver: str) -> Brief:
    """主管审批后标记 published。未审批的简报不得标记 published；系统不直接向会员推送。"""
    if not approver:
        raise ValueError("审批人不能为空")
    brief.status = "published"
    brief.approved_by = approver
    return brief
