"""变异自证：证明门禁（测试）不是恒真。

三相：
  A 相：原代码跑 pytest，全过；
  B 相：两个定向变异，各自必须让目标测试变红——
    M1 收录规则恒真（is_eligible 恒返回 True）：AC3 剔除测试必须失败；
    M2 对外版混入会员名（public 版也写 related_members）：AC2 测试必须失败；
    只认目标断言的失败（检查失败测试名），不只看退出码；
  C 相：原文件 SHA256 未变，重新跑 pytest，全过。

变异在临时复制目录里做，原仓文件只读。临时目录优先用 TMPDIR，/tmp
不足时用家目录（见 setup.sh 的 TMPDIR 处理）。
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_FILES = [
    ROOT / "src" / "intel_brief" / "models.py",
    ROOT / "src" / "intel_brief" / "rules.py",
    ROOT / "src" / "intel_brief" / "brief.py",
    ROOT / "src" / "intel_brief" / "export.py",
]

MUTATIONS = [
    {
        "id": "M1",
        "file": "src/intel_brief/rules.py",
        "old": '    """返回 None 表示可收录，否则返回剔除原因（任务原文措辞）。"""',
        "new": '    """返回 None 表示可收录，否则返回剔除原因（任务原文措辞）。"""\n    return None  # MUTATION M1: eligibility always true',
        "tests": ["tests/test_ac3_exclusion.py"],
        "must_fail": ["test_five_ineligible_items_excluded_with_reasons",
                      "test_excluded_ids_absent_from_all_sections"],
    },
    {
        "id": "M2",
        "file": "src/intel_brief/export.py",
        "old": '    if edition == "staff" and item.related_members:',
        "new": '    if item.related_members:  # MUTATION M2: public leaks members',
        "tests": ["tests/test_ac2_public_no_members.py"],
        "must_fail": ["test_public_md_contains_no_member_name",
                      "test_public_md_has_no_related_members_line",
                      "test_public_pdf_text_contains_no_member_name"],
    },
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_pytest(py: str, cwd: Path, tests: list[str]) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(cwd / "src")
    return subprocess.run(
        [py, "-m", "pytest", "-q", *tests],
        cwd=cwd, env=env, capture_output=True, text=True, timeout=300,
    )


def failed_tests(output: str) -> set[str]:
    names = set()
    for line in output.splitlines():
        m = re.match(r"FAILED tests/\S+::(\w+)", line)
        if m:
            names.add(m.group(1))
        m = re.match(r"tests/\S+::(\w+) FAILED", line)
        if m:
            names.add(m.group(1))
    return names


def main() -> int:
    py = sys.executable
    before = {p: sha256(p) for p in SRC_FILES}

    print("=== A 相：原代码 pytest ===")
    res_a = run_pytest(py, ROOT, ["tests/"])
    print(res_a.stdout[-2000:])
    print(res_a.stderr[-1000:])
    if res_a.returncode != 0:
        print("A 相失败：原代码测试未全过，变异自证无效")
        return 1

    tmp_base = Path(os.environ.get("TMPDIR") or "/tmp")
    work = tmp_base / (".tmp-2245-mutation-%d" % os.getpid())
    if work.exists():
        shutil.rmtree(work)
    try:
        for mut in MUTATIONS:
            print("=== B 相 %s：变异 %s ===" % (mut["id"], mut["file"]))
            shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns(
                ".venv", ".git", "__pycache__", ".pytest_cache", ".tmp-*"))
            target = work / mut["file"]
            text = target.read_text(encoding="utf-8")
            assert mut["old"] in text, "变异锚点未命中：%s" % mut["id"]
            target.write_text(text.replace(mut["old"], mut["new"], 1), encoding="utf-8")
            res_b = run_pytest(py, work, mut["tests"])
            failed = failed_tests(res_b.stdout + res_b.stderr)
            print("失败测试：%s" % sorted(failed))
            missing = [t for t in mut["must_fail"] if t not in failed]
            # PDF 文本测试在无 pdftotext 时 skip，不计入必须失败
            missing = [t for t in missing if "pdf_text" not in t]
            if res_b.returncode == 0:
                print("%s 未变红：变异后测试仍全过，门禁恒真" % mut["id"])
                return 1
            if missing:
                print("%s 变红但目标断言未失败：缺 %s" % (mut["id"], missing))
                return 1
            print("%s 变红，目标断言失败，符合预期" % mut["id"])
            shutil.rmtree(work)
    finally:
        if work.exists():
            shutil.rmtree(work, ignore_errors=True)

    print("=== C 相：原文件未变 + 重跑 pytest ===")
    after = {p: sha256(p) for p in SRC_FILES}
    if before != after:
        print("C 相失败：原文件 SHA256 变了")
        return 1
    res_c = run_pytest(py, ROOT, ["tests/"])
    print(res_c.stdout[-1500:])
    if res_c.returncode != 0:
        print("C 相失败：恢复后测试未全过")
        return 1

    print("MUTATION CHECK: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
