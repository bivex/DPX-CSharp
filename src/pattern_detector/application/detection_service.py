"""Application Service orchestrating C# Pattern Detection use cases."""

from __future__ import annotations

import time
from typing import Sequence

from pattern_detector.adapters.outbound.parsers.native_cs_parser_adapter import NativeCSharpParserAdapter
from pattern_detector.domain.detection import Detection, DetectionReport
from pattern_detector.domain.rules import DEFAULT_RULES, PatternRule
from pattern_detector.ports.inbound import ScanProjectUseCase


class DetectionService(ScanProjectUseCase):
    """Core application service coordinating C# parsing and pattern rule evaluation."""

    def __init__(
        self,
        rules: Sequence[PatternRule] | None = None,
        parser: NativeCSharpParserAdapter | None = None,
    ) -> None:
        self._rules = list(rules) if rules is not None else list(DEFAULT_RULES)
        self._parser = parser or NativeCSharpParserAdapter()

    def scan(
        self,
        project_path: str,
        excludes: Sequence[str] | None = None,
        verbose: bool = False,
    ) -> DetectionReport:
        start_time = time.time()
        model = self._parser.parse_project(project_path, excludes=excludes)

        detections: list[Detection] = []
        for rule in self._rules:
            try:
                results = rule.detect(model)
                detections.extend(results)
            except Exception as ex:
                if verbose:
                    print(f"Warning: Rule {rule.pattern_type.value} failed: {ex}")

        # Sort detections by confidence score descending
        detections.sort(key=lambda d: d.confidence.value, reverse=True)

        end_time = time.time()

        return DetectionReport(
            project_path=project_path,
            detections=detections,
            scanned_files_count=model.total_modules,
            start_time=start_time,
            end_time=end_time,
            metadata={"rule_count": len(self._rules)},
        )
