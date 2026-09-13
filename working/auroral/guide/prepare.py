"""감사 원문에서 표시 문장 목록과 개행을 보존한 영어 작업본을 준비해요."""

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[2]


def visible_lines(text):
    """제목과 사용자 표시 문장이 있는 줄만 골라요."""
    result = []
    front = False
    for i, line in enumerate(text.splitlines()):
        if line == "---":
            front = not front
            continue
        if front:
            if re.match(r"\s*title:", line):
                result.append((i, line.strip()))
            continue
        visible = re.sub(r"<[^>]*>", "", line)
        if re.search(r"[A-Za-z]", visible):
            result.append((i, line.strip()))
    return result


if __name__ == "__main__":
    audit = json.loads(
        (PROJECT / "working/stage1_audit/auroral_guide_sources.json").read_text(
            encoding="utf-8"
        )
    )
    segments = []
    for item in audit["files"]:
        relative = item["member"].removeprefix("assets/auroral/auroral/")
        data = item["english_markdown"].encode("utf-8")
        assert hashlib.sha256(data).hexdigest() == item["sha256"], relative
        path = ROOT / "en_us" / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        segments.append(
            {"path": relative, "lines": visible_lines(item["english_markdown"])}
        )
    (ROOT / "segments.json").write_text(
        json.dumps(segments, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"원문 {len(segments)}페이지, 표시 줄 {sum(len(p['lines']) for p in segments)}개"
    )
