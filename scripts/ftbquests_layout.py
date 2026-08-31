"""ATM10 버전별 FTB Quests 언어 파일 구조와 출력 경로를 제공한다."""

from __future__ import annotations

from pathlib import Path

from version_context import active_output_root

LANG_RELATIVE_ROOT = Path("config/ftbquests/quests/lang")
OUTPUT_LANG_ROOT = active_output_root() / "overrides" / LANG_RELATIVE_ROOT
SUPPORTED_SUFFIXES = (".snbt", ".snbt_merged")


def language_root(instance: Path) -> Path:
    """인스턴스의 FTB Quests 언어 루트를 반환한다."""
    return instance / LANG_RELATIVE_ROOT


def merged_locale_file(instance: Path, locale: str) -> Path:
    """7.1과 같은 단일 병합 언어 파일 경로를 반환한다."""
    return language_root(instance) / f"{locale}.snbt"


def split_locale_root(instance: Path, locale: str) -> Path:
    """8.1과 같은 분할 언어 디렉터리 경로를 반환한다."""
    return language_root(instance) / locale


def split_locale_files(instance: Path, locale: str) -> dict[str, Path]:
    """분할 언어 파일을 locale 디렉터리 기준 상대 경로로 반환한다."""
    root = split_locale_root(instance, locale)
    if not root.is_dir():
        return {}
    return {
        path.relative_to(root).as_posix(): path
        for path in sorted(root.rglob("*"), key=lambda item: item.as_posix().lower())
        if path.is_file() and path.name.endswith(SUPPORTED_SUFFIXES)
    }


def detect_layout(instance: Path) -> str:
    """영어 원문 기준으로 merged, split 또는 혼합 구조를 판정한다."""
    merged = merged_locale_file(instance, "en_us").is_file()
    split = bool(split_locale_files(instance, "en_us"))
    if merged and split:
        return "merged_and_split"
    if merged:
        return "merged"
    if split:
        return "split"
    return "missing"


def output_merged_locale_file(locale: str = "ko_kr") -> Path:
    """검증된 병합 언어 산출물의 저장 경로를 반환한다."""
    return OUTPUT_LANG_ROOT / f"{locale}.snbt"


def output_split_locale_file(relative: str | Path, locale: str = "ko_kr") -> Path:
    """검증된 분할 언어 산출물의 저장 경로를 반환한다."""
    relative_path = Path(relative)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise ValueError(f"분할 언어 파일은 안전한 상대 경로여야 합니다: {relative}")
    return OUTPUT_LANG_ROOT / locale / relative_path
