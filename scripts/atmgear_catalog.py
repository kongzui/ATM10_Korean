#!/usr/bin/env python3
"""Allthemodium·ATM 장비 계열 언어 네임스페이스 목록."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Target:
    """한 JAR에서 전수 검수할 언어 네임스페이스."""

    batch: str
    jar_prefix: str
    namespace: str


TARGETS = (
    Target("allthemodium", "allthemodium-", "allthemodium"),
    Target("allthearcanistgear", "allthearcanistgear-", "allthearcanistgear"),
    Target("allthewizardgear", "allthewizardgear-", "allthewizardgear"),
)
BATCHES = tuple(target.batch for target in TARGETS)
