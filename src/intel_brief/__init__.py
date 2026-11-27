"""会员空间平台 · 每周情报简报编排与导出（ClawHunt #2245，S5-INTEL-028 最小样品）。

纯标准库（导出 PDF 时用 fpdf2 + 系统 Noto CJK 字体）；只用虚构测试数据。
"""

from .brief import Brief, approve, generate_brief
from .export import export_md, export_pdf_bytes
from .models import SECTION_ORDER, Item
from .rules import eligibility_reason, is_eligible, section_sort_key, sort_section

__all__ = [
    "Brief",
    "Item",
    "SECTION_ORDER",
    "approve",
    "eligibility_reason",
    "export_md",
    "export_pdf_bytes",
    "generate_brief",
    "is_eligible",
    "section_sort_key",
    "sort_section",
]
