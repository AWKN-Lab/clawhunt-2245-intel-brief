"""导出：Markdown 与 PDF，员工版 / 对外版。

员工版含“可能相关的会员”；对外版整份不出现任何会员企业名称
（相关会员行整行去掉，不只是置空）。PDF 用 fpdf2 + 系统 Noto CJK 字体
渲染中文；找不到字体时明确报错，不静默降级为缺字 PDF。
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .brief import Brief
from .models import SECTION_ORDER, Item

EDITIONS = ("staff", "public")
EDITION_LABEL = {"staff": "员工版", "public": "对外版"}

# 本机实测存在的 Noto CJK 字体候选路径（按优先级）；fpdf2 接受 .ttc
FONT_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
]
FONT_BOLD_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc",
]


def _find_font(candidates: list[str]) -> str:
    for path in candidates:
        if Path(path).is_file():
            return path
    raise RuntimeError("未找到 CJK 字体（候选：%s），无法导出中文 PDF" % ", ".join(candidates))


def _item_lines(item: Item, edition: str) -> list[str]:
    lines = [
        "### %s" % item.title,
        "",
        "- 发布机构：%s" % item.publisher,
        "- 发布日期：%s" % item.published_date.isoformat(),
        "- 原文链接：%s" % (item.source_url or ""),
        "- 摘要：%s" % item.summary,
        "- 适用对象：%s" % item.audience,
        "- 关键条件与截止日期：%s%s"
        % (item.conditions, "；截止 %s" % item.deadline.isoformat() if item.deadline else "；无截止日期"),
    ]
    if edition == "staff" and item.related_members:
        lines.append("- 可能相关的会员：%s" % "、".join(item.related_members))
    return lines


def export_md(brief: Brief, edition: str) -> str:
    """导出 Markdown 文本。edition 为 staff（员工版）或 public（对外版）。"""
    if edition not in EDITIONS:
        raise ValueError("未知版本：%s（须为 staff 或 public）" % edition)
    lines = [
        "# 会员空间平台每周情报简报 %s（%s）" % (brief.issue_no, EDITION_LABEL[edition]),
        "",
        "收录窗口：%s 至 %s；生成日期：%s；状态：%s"
        % (
            brief.week_start.isoformat(),
            brief.week_end.isoformat(),
            brief.generated_at.isoformat(),
            "已发布（审批人：%s）" % brief.approved_by if brief.status == "published" else "草稿（待主管审批）",
        ),
        "",
        "共收录 %d 条。" % brief.total_items,
        "",
    ]
    for section in SECTION_ORDER:
        items = brief.sections.get(section, [])
        lines.append("## %s（%d 条）" % (section, len(items)))
        lines.append("")
        for item in items:
            lines.extend(_item_lines(item, edition))
            lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def export_pdf_bytes(brief: Brief, edition: str) -> bytes:
    """导出 PDF 字节。依赖 fpdf2；字体缺失时报错，不出缺字 PDF。"""
    if edition not in EDITIONS:
        raise ValueError("未知版本：%s（须为 staff 或 public）" % edition)
    try:
        from fpdf import FPDF
    except ImportError as exc:  # pragma: no cover - 依赖缺失时 setup.sh 已拦
        raise RuntimeError("导出 PDF 需要 fpdf2（pip install -r requirements.txt）") from exc

    font = _find_font(FONT_CANDIDATES)
    try:
        font_bold = _find_font(FONT_BOLD_CANDIDATES)
    except RuntimeError:
        font_bold = font

    pdf = FPDF(format="A4")
    # 固定创建日期：同一次简报两次导出须字节一致，否则 MANIFEST 无法自证
    pdf.set_creation_date(datetime(2026, 11, 27, 12, 0, 0))
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_font("CJK", "", font)
    pdf.add_font("CJK", "B", font_bold)
    pdf.add_page()

    pdf.set_font("CJK", "B", 16)
    pdf.cell(0, 12, "会员空间平台每周情报简报 %s（%s）" % (brief.issue_no, EDITION_LABEL[edition]),
            new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("CJK", "", 10)
    pdf.cell(0, 7, "收录窗口：%s 至 %s；生成日期：%s；共收录 %d 条"
            % (brief.week_start.isoformat(), brief.week_end.isoformat(),
               brief.generated_at.isoformat(), brief.total_items),
            new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    for section in SECTION_ORDER:
        items = brief.sections.get(section, [])
        pdf.set_font("CJK", "B", 13)
        pdf.cell(0, 9, "%s（%d 条）" % (section, len(items)), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("CJK", "", 11)
        for item in items:
            pdf.set_font("CJK", "B", 11)
            pdf.multi_cell(0, 7, item.title, new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("CJK", "", 11)
            for line in _item_lines(item, edition)[2:]:
                pdf.multi_cell(0, 6, line, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
    out = pdf.output()
    return bytes(out)
