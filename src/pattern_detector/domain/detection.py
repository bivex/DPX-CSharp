"""Detection models and scan reporting for C# Pattern Detector."""

from __future__ import annotations

import time
from typing import Any
from pydantic import BaseModel, Field

from pattern_detector.domain.value_objects import (
    Confidence,
    ConfidenceLevel,
    Evidence,
    Location,
    PatternCategory,
    PatternType,
)


class Detection(BaseModel):
    """A detected architectural pattern, design idiom, or hazard in C# code."""

    pattern_type: PatternType
    pattern_category: PatternCategory
    target_name: str
    target_kind: str
    summary: str
    confidence: Confidence
    primary_location: Location | None = None
    related_locations: list[Location] = Field(default_factory=list)
    evidences: list[Evidence] = Field(default_factory=list)

    @property
    def level(self) -> ConfidenceLevel:
        return self.confidence.level


class DetectionReport(BaseModel):
    """Complete architectural analysis report of a C# scan."""

    project_path: str
    detections: list[Detection] = Field(default_factory=list)
    scanned_files_count: int = 0
    start_time: float = Field(default_factory=time.time)
    end_time: float = Field(default_factory=time.time)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def elapsed_seconds(self) -> float:
        return max(0.0001, self.end_time - self.start_time)

    @property
    def total_detections_count(self) -> int:
        return len(self.detections)

    @property
    def summary_by_category(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for d in self.detections:
            cat = d.pattern_category.value
            counts[cat] = counts.get(cat, 0) + 1
        return counts

    @property
    def summary_by_pattern(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for d in self.detections:
            ptype = d.pattern_type.value
            counts[ptype] = counts.get(ptype, 0) + 1
        return counts
