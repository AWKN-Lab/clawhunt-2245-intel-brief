"""生成 MANIFEST.sha256：仓内全部文件（除 MANIFEST 自身与自测输出日志）的 SHA256。

自测输出日志 evidence/selftest-setup-sh-20261127.log 不进清单：
写入即改变自身哈希，无法列入清单自证（见 README）。
.venv / .git / __pycache__ / .pytest_cache 不进仓，不列入清单。
"""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", ".venv", ".tmp-pip", "__pycache__", ".pytest_cache"}
SKIP_FILES = {"MANIFEST.sha256", "evidence/selftest-setup-sh-20261127.log"}


def main() -> int:
    lines = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        rel = str(path.relative_to(ROOT))
        if rel in SKIP_FILES:
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append("%s  %s" % (digest, rel))
    (ROOT / "MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("MANIFEST: %d files" % len(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
