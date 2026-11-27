"""AC1：用 12 条虚构已审批条目生成简报，分节与排序符合规则（有测试）。"""
from conftest import load_sample_brief, load_sample_items

EXPECTED_SECTION_ORDER = ["补贴申报", "资质认定", "税收优惠", "行业动态", "活动通知"]
EXPECTED_COUNTS = {"补贴申报": 3, "资质认定": 3, "税收优惠": 2, "行业动态": 2, "活动通知": 2}


def test_twelve_eligible_items_included():
    brief = load_sample_brief()
    assert brief.total_items == 12


def test_section_order_and_counts():
    brief = load_sample_brief()
    assert list(brief.sections.keys()) == EXPECTED_SECTION_ORDER
    for section, count in EXPECTED_COUNTS.items():
        assert len(brief.sections[section]) == count, section


def test_subsidy_deadline_ascending_then_no_deadline():
    brief = load_sample_brief()
    assert [i.id for i in brief.sections["补贴申报"]] == ["I02", "I01", "I03"]


def test_qualification_deadline_ascending_then_no_deadline():
    brief = load_sample_brief()
    assert [i.id for i in brief.sections["资质认定"]] == ["I05", "I04", "I06"]


def test_tax_deadline_then_no_deadline():
    brief = load_sample_brief()
    assert [i.id for i in brief.sections["税收优惠"]] == ["I07", "I08"]


def test_industry_no_deadline_published_descending():
    brief = load_sample_brief()
    assert [i.id for i in brief.sections["行业动态"]] == ["I10", "I09"]


def test_event_deadline_ascending():
    brief = load_sample_brief()
    assert [i.id for i in brief.sections["活动通知"]] == ["I12", "I11"]


def test_each_item_has_all_eight_fields():
    _, items = load_sample_items()
    for item in items:
        if item.id.startswith("I0") or item.id.startswith("I1"):
            assert item.title and item.publisher and item.published_date
            assert item.source_url and item.summary and item.audience
            assert item.conditions is not None and item.category


def test_all_summaries_within_150_chars():
    _, items = load_sample_items()
    for item in items:
        assert len(item.summary) <= 150, item.id
