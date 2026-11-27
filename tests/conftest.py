"""测试共享：加载样例数据并生成 2026-W45 简报。"""
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from intel_brief import Item, generate_brief  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def _parse_date(s):
    return date.fromisoformat(s) if s else None


def load_sample_items():
    data = json.loads((ROOT / "data" / "sample_items.json").read_text(encoding="utf-8"))
    items = []
    for raw in data["items"]:
        items.append(
            Item(
                id=raw["id"],
                title=raw["title"],
                publisher=raw["publisher"],
                published_date=_parse_date(raw["published_date"]),
                source_url=raw["source_url"],
                summary=raw["summary"],
                audience=raw["audience"],
                conditions=raw["conditions"],
                deadline=_parse_date(raw["deadline"]),
                related_members=tuple(raw.get("related_members", [])),
                category=raw["category"],
                approved=raw["approved"],
                approved_date=_parse_date(raw["approved_date"]),
                already_included=raw["already_included"],
            )
        )
    return data, items


def load_sample_brief():
    data, items = load_sample_items()
    brief = generate_brief(
        items,
        data["issue_no"],
        date.fromisoformat(data["week_start"]),
        date.fromisoformat(data["week_end"]),
        date.fromisoformat(data["as_of"]),
    )
    return brief


MEMBER_NAMES = [
    "蓝山虚构科技有限公司",
    "青竹虚构商贸有限公司",
    "白鹭虚构咨询有限公司",
    "红枫虚构服务有限公司",
    "青松虚构科技有限公司",
]
