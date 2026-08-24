"""Base pattern rule protocol and abstract class for C# pattern detection."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol

from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.pattern import PATTERN_CATALOG
from pattern_detector.domain.value_objects import (
    Confidence,
    Evidence,
    Location,
    PatternType,
)


class PatternRule(Protocol):
    @property
    def pattern_type(self) -> PatternType: ...
    def detect(self, model: CodeModel) -> list[Detection]: ...


class BasePatternRule(ABC):
    @property
    @abstractmethod
    def pattern_type(self) -> PatternType:
        raise NotImplementedError

    @abstractmethod
    def detect(self, model: CodeModel) -> list[Detection]:
        raise NotImplementedError

    def _create_detection(
        self,
        target_name: str,
        target_kind: str,
        evidences: list[Evidence],
        summary: str | None = None,
        location: Location | None = None,
        related_locations: list[Location] | None = None,
    ) -> Detection:
        entry = PATTERN_CATALOG[self.pattern_type]
        if not evidences:
            score = 0.5
        else:
            score = min(0.95, sum(e.weight for e in evidences) / len(evidences) + 0.1 * min(len(evidences), 3))
        summary_text = summary or f"{entry.name} detected on {target_kind} '{target_name}'"
        return Detection(
            pattern_type=self.pattern_type,
            pattern_category=entry.category,
            target_name=target_name,
            target_kind=target_kind,
            summary=summary_text,
            confidence=Confidence(value=score),
            primary_location=location,
            related_locations=related_locations or [],
            evidences=evidences,
        )
