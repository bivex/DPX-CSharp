"""Outbound port interfaces for reporting and persistence."""

from __future__ import annotations

from typing import Protocol
from pattern_detector.domain.detection import DetectionReport


class ReportFormatterPort(Protocol):
    def format(self, report: DetectionReport) -> str: ...


class ResultRepositoryPort(Protocol):
    def save(self, report: DetectionReport, target_path: str) -> None: ...
