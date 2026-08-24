"""Code Quality, Complexity, and SOLID Principles Rules for C# / .NET."""

from __future__ import annotations

import re
from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class GodClassSrpRule(BasePatternRule):
    """Detects God Class / Single Responsibility Principle (SRP) violations (> 350 LOC)."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.GOD_CLASS_SRP

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            if m.line_count > 350:
                evidences = [
                    Evidence(
                        description=f"Class module '{m.name}' spans {m.line_count} LOC, exceeding SRP threshold (350 LOC)",
                        weight=0.85,
                        rule_code="SOLID_GOD_CLASS_SRP",
                        location=m.location,
                    )
                ]
                detections.append(self._create_detection(
                    target_name=f"{m.namespace}.{m.name}",
                    target_kind="god_class_module",
                    evidences=evidences,
                    location=m.location,
                ))
        return detections


class CyclomaticComplexityKissRule(BasePatternRule):
    """Detects High Cyclomatic Complexity / KISS violations (> 10 branch decision points)."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.CYCLOMATIC_COMPLEXITY_KISS

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            raw = m.raw_source
            branches = len(re.findall(r"\b(if|else if|case|while|for|foreach|catch|\?\?|\?\:)\b", raw))
            if branches >= 12:
                evidences = [
                    Evidence(
                        description=f"Module '{m.name}' has estimated cyclomatic complexity score of {branches} branches (threshold: 12)",
                        weight=0.80,
                        rule_code="SOLID_CYCLOMATIC_COMPLEXITY_KISS",
                        location=m.location,
                    )
                ]
                detections.append(self._create_detection(
                    target_name=f"{m.namespace}.{m.name}",
                    target_kind="complex_module",
                    evidences=evidences,
                    location=m.location,
                ))
        return detections


class DuplicateCodeDryRule(BasePatternRule):
    """Detects repeated structural code sequences across modules violating DRY."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.DUPLICATE_CODE_DRY

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        seen_lines: dict[str, str] = {}
        for m in model.all_modules():
            clean_lines = [l.strip() for l in m.raw_source.splitlines() if len(l.strip()) > 30 and not l.strip().startswith("//")]
            for l in clean_lines:
                if l in seen_lines and seen_lines[l] != m.path:
                    evidences = [
                        Evidence(
                            description=f"Duplicate code sequence identified across modules `{seen_lines[l]}` and `{m.path}`",
                            weight=0.70,
                            rule_code="SOLID_DUPLICATE_CODE_DRY",
                            location=m.location,
                        )
                    ]
                    detections.append(self._create_detection(
                        target_name=f"{m.namespace}.{m.name}",
                        target_kind="duplicate_logic_module",
                        evidences=evidences,
                        location=m.location,
                    ))
                    break
                seen_lines[l] = m.path
        return detections


class CircularNamespaceDependencyRule(BasePatternRule):
    """Detects cyclic bidirectional `using` dependencies between namespaces."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.CIRCULAR_NAMESPACE_DEPENDENCY

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        ns_imports: dict[str, set[str]] = {}
        for m in model.all_modules():
            if m.namespace:
                ns_imports.setdefault(m.namespace, set()).update(m.usings)

        reported_cycles = set()
        for ns, usings in ns_imports.items():
            for target_ns in usings:
                if target_ns in ns_imports and ns in ns_imports[target_ns] and ns != target_ns:
                    cycle_key = tuple(sorted([ns, target_ns]))
                    if cycle_key not in reported_cycles:
                        reported_cycles.add(cycle_key)
                        evidences = [
                            Evidence(
                                description=f"Circular namespace dependency cycle detected: `{ns}` ⇄ `{target_ns}`",
                                weight=0.85,
                                rule_code="SOLID_CIRCULAR_NAMESPACE_IMPORT",
                            )
                        ]
                        detections.append(self._create_detection(
                            target_name=f"{ns} ⇄ {target_ns}",
                            target_kind="circular_namespace_cycle",
                            evidences=evidences,
                        ))
        return detections
