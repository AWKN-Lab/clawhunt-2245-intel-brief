# clawhunt-2245-intel-brief

ClawHunt #2245（S5-INTEL-028）最小可验证样品：会员空间平台 · 每周情报简报编排与
Markdown、PDF 导出。

- 每周一 08:00 生成本期草稿（期号如 2026-W45），收录上周一至周日审批通过、
  未过期、未被收录过的条目；
- 按政策类型分节（补贴申报、资质认定、税收优惠、行业动态、活动通知），节内
  有截止日期的按截止日期升序、无截止日期的按发布日期降序；
- 每条结构：标题、发布机构、发布日期、原文链接、摘要（≤ 150 字）、适用对象、
  关键条件与截止日期、可能相关的会员；
- 员工版含匹配会员企业名，对外版不含任何会员信息；
- 导出 GET /api/intel/briefs/{id}/export?format=md|pdf&edition=staff|public
  对应的两种格式（本样品为离线导出函数；接口层见“对接点”）；
- 简报须主管审批后才能标记 published，系统不直接向会员推送；
- 编排时剔除缺少原文链接或已过期的条目并记录原因。

只用虚构测试数据，不出现真实企业名称与任何真实个人信息。

## 一键复跑

```bash
bash setup.sh
# 预期：SELFTEST: PASS
```

setup.sh 依次做四件事：生成虚构样例简报（两种版本 × 两种格式）、跑 pytest、
跑变异自证、核对 MANIFEST。首次运行会建本地 `.venv` 并安装
`requirements.txt`（pytest、fpdf2）；PDF 渲染用系统 Noto CJK 字体
（`/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc`），找不到时导出
明确报错，不出缺字 PDF。

## 结构

```
src/intel_brief/
  models.py   Item 模型（摘要 ≤ 150 字、政策类型白名单、已审批须有审批日期）
  rules.py    收录规则（5 条缺一即剔除并记录原因）与节内排序规则
  brief.py    生成简报（分节排序 + 剔除留痕）与主管审批标记
  export.py   Markdown / PDF 导出（员工版 / 对外版）
data/sample_items.json   12 条合格虚构条目 + 5 条应剔除条目
examples/                样例简报 2026-W45：员工版 / 对外版 × md / pdf
tests/                   42 项测试（AC1 9 项、AC2 6 项、AC3 11 项、AC4 7 项、通用 9 项）
scripts/
  generate_sample.py     生成 examples/ 样例
  mutation_check.py      变异自证（三相）
  make_manifest.py       生成 MANIFEST.sha256
evidence/                原始日志（pytest、变异自证、一键复跑）
```

## 实测结果（Python 3.12.3，pytest 9.2.0，fpdf2 2.9.0）

- pytest：42 passed
- 变异自证：MUTATION CHECK: PASS（M1 收录恒真后 AC3 测试 8 项变红；
  M2 对外版混入会员名后 AC2 测试 3 项变红；原文件 SHA256 未变，重跑全过）
- 一键复跑：SELFTEST: PASS
- MANIFEST：全部文件 sha256sum -c 全 OK（MANIFEST 自身与自测输出日志
  evidence/selftest-setup-sh-20261127.log 不进清单，见下）
- 全新克隆验证：HEAD 待推送后补记

样例简报 2026-W45：收录 12 条（补贴申报 3、资质认定 3、税收优惠 2、行业动态 2、
活动通知 2），剔除 5 条（X01 已过期、X02 缺少原文链接、X03 已被以往期次收录过、
X04 未审批通过、X05 审批日期不在收录窗口内）。PDF 为 A4、3 页；对外版 md 与 pdf
经逐字核对不含任何会员企业名称。

## 收录与排序规则（任务原文的机械实现）

收录须同时满足：已审批通过；审批日期落在收录窗口（上周一至周日）内；
有原文链接；未过期（无截止日期视为未过期；有截止日期的须不早于生成日）；
未被以往期次收录过。缺一即剔除，原因逐条记录在 `Brief.excluded`。

排序：节内先排有截止日期的条目（截止日期升序），再排无截止日期的条目
（发布日期降序）。分节顺序固定为补贴申报、资质认定、税收优惠、行业动态、
活动通知。

## 对接点（生产集成时）

- 定时任务：每周一 08:00 调用 `generate_brief`，期号格式 `YYYY-Www`；
- 数据源：条目来自审批通过的情报库（本样品用 `data/sample_items.json` 静态数据代替）；
- 导出接口：`GET /api/intel/briefs/{id}/export?format=md|pdf&edition=staff|public`
  对应 `export_md` / `export_pdf_bytes`；
- 审批：`approve(brief, approver)` 后状态为 published；未审批不得标记 published；
  系统不直接向会员推送，由员工按渠道发布；
- PDF 字体：生产环境须装 Noto CJK（或同等 CJK 字体），否则导出报错；
  PDF 创建日期固定为 2026-11-27 12:00:00，同一次简报两次导出字节一致。

## 已知限制

- 本样品不含 FastAPI 接口层、数据库与定时调度器，只实现编排、导出与规则；
- 摘要长度按字符数计，不做分词；
- PDF 只用 Noto Sans CJK 常规与粗体两档字重；
- 会员名去重只在导出层做字符串级剔除：对外版整行去掉“可能相关的会员”，
  不做语义级脱敏。
