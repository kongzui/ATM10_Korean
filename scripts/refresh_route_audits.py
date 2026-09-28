#!/usr/bin/env python3
"""검증된 선택 적용으로 바뀐 인스턴스 파일의 해시만 표시 경로 감사에 반영해요.

각 모드의 `display_audit.json`은 FTB Quests·KubeJS 전체 파일 해시를 기록해요. 재검수 계열을
적용하면 우리가 덮어쓴 파일의 해시가 바뀌므로, 적용 기록에 있는 경로만 갱신하고 참조 조사
결과(`matches`)와 파일 수(`counts`)가 그대로인지 확인해요. 그 밖의 차이가 있으면 멈춰요.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from local_paths import PROJECT_ROOT, resolve_source_root
from verify_ad_astra_translation import scan_instance_routes

AUDITS = {
    "working/ad_astra/display_audit.json": None,
    "working/logisticsnetworks/display_audit.json": "verify_logisticsnetworks_translation",
    "working/stepcrafter/display_audit.json": "verify_stepcrafter_translation",
    "working/betteradvancedtooltips/display_audit.json": (
        "verify_betteradvancedtooltips_translation"
    ),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("apply_reports", nargs="+", type=Path)
    args = parser.parse_args()

    applied: set[str] = set()
    for report_path in args.apply_reports:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        runs = report.get("runs", [report])
        for run in runs:
            if run.get("status") != "applied_and_verified":
                raise ValueError(f"검증된 적용 기록이 아니에요: {report_path}")
            for target in run["targets"]:
                if target["unexpected_changes"]:
                    raise ValueError(f"예상 밖 변경이 있는 적용 기록: {report_path}")
                applied.update(target["changed_paths"])

    instance = resolve_source_root()
    for relative, module_name in AUDITS.items():
        path = PROJECT_ROOT / relative
        audit = json.loads(path.read_text(encoding="utf-8"))
        pattern = None
        if module_name:
            pattern = __import__(module_name).ROUTE_PATTERN
        current = (
            scan_instance_routes(instance, pattern)
            if pattern
            else scan_instance_routes(instance)
        )
        if (
            current["counts"] != audit["counts"]
            or current["matches"] != audit["matches"]
        ):
            raise ValueError(f"{relative}: 참조 조사 결과가 바뀌어 다시 검수해야 해요")
        changed = {
            key
            for key in set(audit["source_sha256"]) | set(current["source_sha256"])
            if audit["source_sha256"].get(key) != current["source_sha256"].get(key)
        }
        if changed - applied:
            raise ValueError(
                f"{relative}: 적용 기록 밖 변경 {sorted(changed - applied)}"
            )
        audit["source_sha256"] = current["source_sha256"]
        path.write_text(
            json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(relative, len(changed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
