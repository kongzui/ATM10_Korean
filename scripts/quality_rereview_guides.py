#!/usr/bin/env python3
"""8.1 품질 재검수 계열의 가이드 조각 교체 수정본을 검증하고 산출물과 작업 원본에 반영한다.

수정본은 `working/quality_rereview/<계열>/guides/*.json`에 두며 형식은
`{"<네임스페이스>/<가이드 상대 경로>": [{"old": "한 줄 조각", "new": "새 조각"}]}`이다.
조각은 파일에서 정확히 한 번 나와야 하며, 용어 일괄 교체처럼 모두 바꿀 때만 `"all": true`를 붙인다.
줄바꿈을 섞어 쓰는 가이드 파일이 있어 한 줄 조각만 바꾸고 파일의 줄바꿈 바이트는 그대로 둔다.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from quality_rereview_quests import STYLE_SIGNALS
from verify_quality_rereview import git_text
from verify_quality_rereview import markdown_guide_errors
from version_context import active_output_root
from version_context import active_report_dir

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REREVIEW_ROOT = PROJECT_ROOT / "working/quality_rereview"


def read_text(path: Path) -> str:
    """줄바꿈 바이트를 바꾸지 않고 읽는다."""
    with path.open(encoding="utf-8", newline="") as file:
        return file.read()


def replace_once(text: str, old: str, new: str, every: bool = False) -> str | None:
    """조각이 정확히 한 번(every면 한 번 이상) 나오면 바꾼 결과를, 아니면 None을 돌려준다."""
    count = text.count(old)
    if count == 0 or (count != 1 and not every):
        return None
    return text.replace(old, new)


def load_revisions(root: Path) -> tuple[dict[str, list[dict]], list[str]]:
    """여러 워커의 수정본을 합치고, 같은 파일의 교체는 파일 순서대로 이어 붙인다."""
    merged: dict[str, list[dict]] = {}
    errors: list[str] = []
    for path in sorted((root / "guides").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for target, edits in data.items():
            for edit in edits:
                old, new = edit.get("old"), edit.get("new")
                if not isinstance(old, str) or not isinstance(new, str) or old == new:
                    errors.append(f"{path.name}:{target}: old/new가 올바르지 않아요")
                elif "\n" in old + new or "\r" in old + new:
                    errors.append(
                        f"{path.name}:{target}: 조각에 줄바꿈이 있어요 {old[:40]}"
                    )
                else:
                    merged.setdefault(target, []).append(
                        {"old": old, "new": new, "all": edit.get("all") is True}
                    )
    return merged, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("family", help="working/quality_rereview 아래 계열 폴더 이름")
    parser.add_argument("--write-output", action="store_true")
    args = parser.parse_args()

    root = REREVIEW_ROOT / args.family
    scope = json.loads((root / "scope.json").read_text(encoding="utf-8"))
    roots: dict[str, dict[str, str]] = scope.get("guide_roots", {})
    allowed = set(scope.get("guide_files", []))
    revisions, errors = load_revisions(root)
    output_root = active_output_root()

    writes: dict[Path, str] = {}
    report_files: dict[str, Any] = {}
    for target, edits in sorted(revisions.items()):
        namespace, _, relative = target.partition("/")
        if namespace not in roots:
            errors.append(f"{target}: 범위에 없는 네임스페이스예요")
            continue
        output_relative = f"{roots[namespace]['output']}/{relative}"
        if output_relative not in allowed:
            errors.append(f"{target}: 범위의 guide_files에 없어요")
            continue
        output_path = output_root / output_relative
        working_path = PROJECT_ROOT / roots[namespace]["working"] / relative
        text = read_text(output_path)
        working = read_text(working_path) if working_path.is_file() else None
        for edit in edits:
            replaced = replace_once(text, edit["old"], edit["new"], edit["all"])
            if replaced is None:
                errors.append(
                    f"{target}: 산출물에서 한 번만 나오지 않아요: {edit['old']}"
                )
                continue
            text = replaced
            if working is not None:
                replaced = replace_once(working, edit["old"], edit["new"], edit["all"])
                if replaced is None:
                    errors.append(
                        f"{target}: 작업 원본에서 한 번만 나오지 않아요: {edit['old']}"
                    )
                else:
                    working = replaced
        baseline = git_text(scope["baseline_commit"], output_relative)
        errors.extend(markdown_guide_errors(text, baseline, target))
        writes[output_path] = text
        if working is not None:
            writes[working_path] = working
        report_files[target] = {
            "edits": len(edits),
            "style_signals": [signal for signal in STYLE_SIGNALS if signal in text],
        }

    signals: dict[str, list[str]] = {}
    for namespace, guide_root in roots.items():
        for path in sorted((output_root / guide_root["output"]).rglob("*.md")):
            key = f"{namespace}/{path.relative_to(output_root / guide_root['output']).as_posix()}"
            text = writes.get(path) or read_text(path)
            hits = [signal for signal in STYLE_SIGNALS if signal in text]
            if hits:
                signals[key] = hits

    report = {
        "family": args.family,
        "guide_files": len(allowed),
        "revised_files": len(report_files),
        "edits": sum(item["edits"] for item in report_files.values()),
        "files": report_files,
        "remaining_style_signals": signals,
        "errors": errors,
    }
    report_path = active_report_dir() / f"quality_rereview_{args.family}_guides.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {key: value for key, value in report.items() if key != "files"},
            ensure_ascii=False,
            indent=2,
        )
    )
    if errors:
        return 1
    if args.write_output:
        for path, text in writes.items():
            with path.open("w", encoding="utf-8", newline="") as file:
                file.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
