"""数据模型：情报条目。只用虚构测试数据，不出现真实企业与个人信息。"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

# 分节顺序：任务原文“补贴申报、资质认定、税收优惠……行业动态、活动通知”
SECTION_ORDER = ["补贴申报", "资质认定", "税收优惠", "行业动态", "活动通知"]

MAX_SUMMARY_CHARS = 150


@dataclass(frozen=True)
class Item:
    """一条待编排的情报条目。"""

    id: str
    title: str
    publisher: str
    published_date: date
    source_url: str | None
    summary: str
    audience: str
    conditions: str
    deadline: date | None
    related_members: tuple[str, ...] = ()
    category: str = "行业动态"
    approved: bool = False
    approved_date: date | None = None
    already_included: bool = False

    def __post_init__(self) -> None:
        if self.category not in SECTION_ORDER:
            raise ValueError("未知政策类型：%s（须为 %s 之一）" % (self.category, SECTION_ORDER))
        if len(self.summary) > MAX_SUMMARY_CHARS:
            raise ValueError(
                "摘要超过 %d 字：%s（%d 字）" % (MAX_SUMMARY_CHARS, self.id, len(self.summary))
            )
        if self.approved and self.approved_date is None:
            raise ValueError("已审批条目必须有审批日期：%s" % self.id)
