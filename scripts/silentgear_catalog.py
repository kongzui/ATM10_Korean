#!/usr/bin/env python3
"""Silent Gear 계열 언어 네임스페이스 목록."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Target:
    """한 JAR에서 전수 검수할 언어 네임스페이스."""

    batch: str
    jar_prefix: str
    namespace: str


TARGETS = (
    Target("silentgear", "silent-gear-", "silentgear"),
    Target("silentlib", "silent-lib-", "silentlib"),
    Target("silentgems", "silentgems-", "silentgems"),
    Target("sgearmetalworks", "sgearmetalworks-", "sgearmetalworks"),
)
BATCHES = tuple(target.batch for target in TARGETS)
