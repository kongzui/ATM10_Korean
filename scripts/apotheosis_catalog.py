"""Apotheosis 계열과 직접 연동 언어 키의 번역 대상 정의."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Target:
    """설치 JAR 하나와 그 안에서 이번 단계에 처리할 언어 키."""

    batch: str
    jar_prefix: str
    namespace: str
    key_patterns: tuple[str, ...] = ()

    def includes(self, key: str) -> bool:
        """전체 네임스페이스 또는 직접 연동 키만 선택한다."""
        if key.startswith("comment_"):
            return False
        return not self.key_patterns or any(
            re.search(pattern, key, re.IGNORECASE) for pattern in self.key_patterns
        )


TARGETS = (
    Target("core", "Apotheosis-", "apotheosis"),
    Target("attributes", "ApothicAttributes-", "apothic_attributes"),
    Target("enchanting", "ApothicEnchanting-", "apothic_enchanting"),
    Target("spawners", "ApothicSpawners-", "apothic_spawners"),
    Target(
        "integrations",
        "create-enchantment-industry-",
        "create_enchantment_industry",
        (
            r"affix",
            r"apotheot",
            r"bookshelf\.(?:arcana|eterna|quanta)",
            r"infuser\.stats\.(?:arcana|eterna|quanta)",
            r"gem_cutter",
            r"^create_enchantment_industry\.gui\.goggles\.blaze_composer\.",
            r"^create_enchantment_industry\.ponder\.(?:brass_bookshelf|bulk_salvaging|creative_bookshelf|infuser)",
        ),
    ),
    Target(
        "integrations",
        "irons_spellbooks-",
        "irons_spellbooks",
        (
            r"^item\.apotheosis\.gem\.",
            r"^text\.apotheosis\.",
            r"^affix\.irons_spellbooks:",
        ),
    ),
)

BATCHES = ("core", "attributes", "enchanting", "spawners", "integrations")
