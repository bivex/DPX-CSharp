"""Rules for C# Type System, Records, Pattern Matching, and Generics."""

from __future__ import annotations

import re
from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class RecordStructImmutabilityRule(BasePatternRule):
    """Detects C# Records and Readonly Record Structs for immutable value modeling."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.RECORD_STRUCT_IMMUTABILITY

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            for rec_name, rec in m.records.items():
                evidences = [
                    Evidence(
                        description=f"{'Readonly ' if rec.is_readonly else ''}Record {'Struct' if rec.is_struct else 'Class'} '{rec_name}' provides compiler-synthesized value equality and non-destructive mutation (`with`)",
                        weight=0.90,
                        rule_code="CSHARP_RECORD_IMMUTABILITY",
                        location=rec.location,
                    )
                ]
                detections.append(self._create_detection(
                    target_name=f"{m.namespace}.{rec_name}",
                    target_kind="record_declaration",
                    evidences=evidences,
                    location=rec.location,
                ))
        return detections


class PatternMatchingSwitchRule(BasePatternRule):
    """Detects C# 8+ switch expressions, relational, and property pattern matching."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.PATTERN_MATCHING_SWITCH

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        switch_expr_pattern = re.compile(r"(\w+)\s+switch\s*\{", re.MULTILINE)
        for m in model.all_modules():
            raw = m.raw_source
            for match in switch_expr_pattern.finditer(raw):
                target = match.group(1)
                line_no = raw[:match.start()].count("\n") + 1
                evidences = [
                    Evidence(
                        description=f"Switch expression pattern matching on `{target}` replaces imperative if-else branches with total relational pattern matching",
                        weight=0.85,
                        rule_code="CSHARP_SWITCH_EXPRESSION",
                        location=m.location,
                    )
                ]
                detections.append(self._create_detection(
                    target_name=f"{m.name}.{target}_Switch",
                    target_kind="switch_expression",
                    evidences=evidences,
                    location=m.location,
                ))
        return detections


class PrimaryConstructorRule(BasePatternRule):
    """Detects C# 12+ primary constructors on classes and structs."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.PRIMARY_CONSTRUCTOR

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            for cls_name, cls in m.classes.items():
                if cls.has_primary_constructor and cls.constructor_params:
                    evidences = [
                        Evidence(
                            description=f"Class '{cls_name}' utilizes C# Primary Constructor with {len(cls.constructor_params)} parameter(s) binding directly into class body",
                            weight=0.90,
                            rule_code="CSHARP_PRIMARY_CONSTRUCTOR",
                            location=cls.location,
                        )
                    ]
                    detections.append(self._create_detection(
                        target_name=f"{m.namespace}.{cls_name}",
                        target_kind="primary_constructor_class",
                        evidences=evidences,
                        location=cls.location,
                    ))
        return detections


class GenericVarianceInOutRule(BasePatternRule):
    """Detects `out T` (covariance) and `in T` (contravariance) generic type variance."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.GENERIC_VARIANCE_IN_OUT

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            for iface_name, iface in m.interfaces.items():
                if iface.has_in_out_variance:
                    evidences = [
                        Evidence(
                            description=f"Generic interface '{iface_name}' defines explicit covariance (`out`) or contravariance (`in`) variance modifiers",
                            weight=0.90,
                            rule_code="CSHARP_GENERIC_VARIANCE",
                            location=iface.location,
                        )
                    ]
                    detections.append(self._create_detection(
                        target_name=f"{m.namespace}.{iface_name}",
                        target_kind="variant_generic_interface",
                        evidences=evidences,
                        location=iface.location,
                    ))
        return detections


class ExpressionTreeLinqRule(BasePatternRule):
    """Detects `Expression<Func<T, bool>>` expression trees and LINQ query transformations."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.EXPRESSION_TREE_LINQ

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            raw = m.raw_source
            if "Expression<Func<" in raw or "Expression<Action<" in raw:
                evidences = [
                    Evidence(
                        description=f"Module '{m.name}' composes `Expression<Func<...>>` expression trees for metaprogramming / query translation",
                        weight=0.85,
                        rule_code="CSHARP_EXPRESSION_TREE_LINQ",
                        location=m.location,
                    )
                ]
                detections.append(self._create_detection(
                    target_name=f"{m.namespace}.{m.name}",
                    target_kind="expression_tree_module",
                    evidences=evidences,
                    location=m.location,
                ))
        return detections
