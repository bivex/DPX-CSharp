"""Inbound port interfaces for C# Pattern Detection use cases."""

from __future__ import annotations

from typing import Protocol, Sequence
from pattern_detector.domain.detection import DetectionReport


class ScanProjectUseCase(Protocol):
    def scan(
        self,
        project_path: str,
        excludes: Sequence[str] | None = None,
        verbose: bool = False,
    ) -> DetectionReport: ...
