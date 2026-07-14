"""Sophisticated 저장소 계열 번역 대상 정의."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Target:
    """설치 JAR 하나와 그 안의 번역 네임스페이스."""

    batch: str
    jar_prefix: str
    namespace: str | None


TARGETS = (
    Target("core", "sophisticatedcore-", "sophisticatedcore"),
    Target("backpacks", "sophisticatedbackpacks-", "sophisticatedbackpacks"),
    Target("backpacks", "sophisticatedbackpackscreateintegration-", None),
    Target("storage", "sophisticatedstorage-", "sophisticatedstorage"),
    Target("storage", "sophisticatedstoragecreateintegration-", None),
    Target("storage", "sophisticatedstorageinmotion-", "sophisticatedstorageinmotion"),
)

BATCHES = ("core", "backpacks", "storage")
