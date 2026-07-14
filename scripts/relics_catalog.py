#!/usr/bin/env python3
"""Relics·Artifacts 계열 언어 네임스페이스 목록."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Target:
    """한 JAR에서 전수 검수할 언어 네임스페이스."""

    batch: str
    jar_prefix: str
    namespace: str


TARGETS = (
    Target("artifacts", "artifacts-neoforge-", "artifacts"),
    Target("relics", "relics-", "relics"),
    Target(
        "reliquified_artifacts",
        "reliquified_artifacts-",
        "reliquified_artifacts",
    ),
)
BATCHES = tuple(target.batch for target in TARGETS)
