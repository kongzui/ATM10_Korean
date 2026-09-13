"""저장한 검수 번역을 원문 줄에 대응시켜 허용된 작업 폴더에만 만들어요."""

import hashlib
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[2]
sys.path.insert(0, str(PROJECT / "scripts"))

import build_ae2_guide as guide  # noqa: E402
from build_ae2_addon_guides import validate_tag_nesting  # noqa: E402
from verify_stage1_translation import check_value  # noqa: E402


def main():
    segments = json.loads((ROOT / "segments.json").read_text(encoding="utf-8"))
    translations = {}
    for path in sorted(ROOT.glob("batch*.json")):
        batch = json.loads(path.read_text(encoding="utf-8"))
        assert not translations.keys() & batch.keys(), path
        translations.update(batch)
    checked = []
    for page in segments:
        relative = page["path"]
        if relative not in translations:
            continue
        source_bytes = (ROOT / "en_us" / relative).read_bytes()
        source = source_bytes.decode("utf-8")
        lines = source.splitlines(keepends=True)
        translated_lines = translations[relative]
        assert len(translated_lines) == len(page["lines"]), relative
        for (index, original), translated in zip(page["lines"], translated_lines):
            assert lines[index].strip() == original, (relative, index)
            prefix = re.match(r"[ \t]*", lines[index])[0]
            newline = lines[index][len(lines[index].rstrip("\r\n")) :]
            lines[index] = prefix + translated + newline
        target = "".join(lines)
        errors = guide.validate_pair(
            relative, source.replace("\r\n", "\n"), target.replace("\r\n", "\n")
        )
        errors.extend(validate_tag_nesting(relative, target))
        assert not errors, errors
        check_value(relative, source, target)
        for old, new in zip(source.splitlines(), target.splitlines()):
            assert bool(old.strip()) == bool(new.strip()), relative
            assert old.count("**") == new.count("**"), relative
            if old.lstrip().startswith("|"):
                assert old.count("|") == new.count("|"), relative
        output = ROOT / "ko_kr" / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        target_bytes = target.encode("utf-8")
        if not output.exists() or output.read_bytes() != target_bytes:
            output.write_bytes(target_bytes)
        checked.append(
            {
                "path": relative,
                "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
                "target_sha256": hashlib.sha256(target_bytes).hexdigest(),
                "visible_lines": len(translated_lines),
                "validation_errors": [],
            }
        )
    (ROOT / "progress.json").write_text(
        json.dumps(
            {
                "completed_pages": len(checked),
                "total_pages": len(segments),
                "entries": checked,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"검증 및 저장: {len(checked)}/{len(segments)}페이지")


if __name__ == "__main__":
    main()
