# 验收证据（逐字输出）

ClawHunt #2245（S5-INTEL-028）最小样品。以下输出均为实跑原始日志逐字摘录，
完整日志在 `evidence/`。

## 样例生成

```
wrote brief-2026-W45-staff.md (6257 bytes)
wrote brief-2026-W45-staff.pdf (113690 bytes)
wrote brief-2026-W45-public.md (5972 bytes)
wrote brief-2026-W45-public.pdf (110671 bytes)
brief 2026-W45: 12 items included, 5 excluded
excluded X01: 已过期
excluded X02: 缺少原文链接
excluded X03: 已被以往期次收录过
excluded X04: 未审批通过
excluded X05: 审批日期不在收录窗口内
```

## pytest（42 passed）

```
..........................................                               [100%]
42 passed in 20.60s
```

分布：AC1 分节与排序 9 项、AC2 对外版无会员名 6 项、AC3 剔除规则 11 项、
AC4 两种格式导出 7 项、通用行为 9 项。完整日志见 evidence/pytest-20261127.log。

## 变异自证（MUTATION CHECK: PASS）

```
=== B 相 M1：变异 src/intel_brief/rules.py ===
失败测试：['test_already_included_rejected', 'test_approved_outside_window_rejected',
'test_empty_link_rejected', 'test_excluded_ids_absent_from_all_sections',
'test_expired_item_rejected', 'test_five_ineligible_items_excluded_with_reasons',
'test_missing_link_rejected', 'test_not_approved_rejected']
M1 变红，目标断言失败，符合预期
=== B 相 M2：变异 src/intel_brief/export.py ===
失败测试：['test_public_md_contains_no_member_name',
'test_public_md_has_no_related_members_line',
'test_public_pdf_text_contains_no_member_name']
M2 变红，目标断言失败，符合预期
=== C 相：原文件未变 + 重跑 pytest ===
42 passed in 12.38s

MUTATION CHECK: PASS
```

完整日志见 evidence/mutation-20261127.log。

## 一键复跑（SELFTEST: PASS）

```
=== 1/4 生成虚构样例简报（两种版本 × 两种格式）===
=== 2/4 自测 pytest ===
=== 3/4 变异自证（应 MUTATION CHECK: PASS）===
=== 4/4 核对 MANIFEST ===
SELFTEST: PASS
```

完整日志见 evidence/selftest-setup-sh-20261127.log。

## 全新克隆验证

HEAD 3f6566fcae77ad3eb2a0338c277bd4745f1e9db3 上 bash setup.sh 实测 SELFTEST: PASS。

## 对外版逐字核对（不含任何会员企业名称）

对外版 PDF 前 8 行（pdftotext 提取）：

```
会员空间平台每周情报简报 2026-W45（对外版）
收录窗口：2026-11-02 至 2026-11-08；生成日期：2026-11-09；共收录 12 条

补贴申报（3 条）
虚构小微企业创新券申领办法发布
- 发布机构：虚构市科技主管部门
- 发布日期：2026-11-04
- 原文链接：https://example.invalid/gov/2026/chuang-xin-quan
```

5 个虚构会员企业名（蓝山虚构科技有限公司、青竹虚构商贸有限公司、
白鹭虚构咨询有限公司、红枫虚构服务有限公司、青松虚构科技有限公司）
在对外版 md 与 pdf 中出现次数均为 0；在员工版 md 与 pdf 中各出现 1 次以上。

## MANIFEST

25 个文件，sha256sum -c 全 OK（MANIFEST 自身与自测输出日志
evidence/selftest-setup-sh-20261127.log 不进清单）。
