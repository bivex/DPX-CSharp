"""Creational GoF Design Pattern Rules for C# / .NET."""

from __future__ import annotations

import re
from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class AbstractFactoryRule(BasePatternRule):
    """Detects Abstract Factory: interfaces declaring multiple Create* methods for product families."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.ABSTRACT_FACTORY

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            for iface_name, iface in m.interfaces.items():
                create_methods = [mth for mth in iface.methods if mth.startswith("Create")]
                if len(create_methods) >= 2 or ("Factory" in iface_name and create_methods):
                    evidences = [
                        Evidence(
                            description=f"Interface '{iface_name}' declares {len(create_methods)} `Create*()` factory methods — Abstract Factory contract",
                            weight=0.85,
                            rule_code="GOF_ABSTRACT_FACTORY_INTERFACE",
                            location=iface.location,
                        )
                    ]
                    detections.append(self._create_detection(
                        target_name=f"{m.namespace}.{iface_name}",
                        target_kind="abstract_factory_interface",
                        evidences=evidences,
                        location=iface.location,
                    ))
            for cls_name, cls in m.classes.items():
                if "Factory" in cls_name and (cls.implements_list or "Abstract" in cls_name):
                    evidences = [
                        Evidence(
                            description=f"Class '{cls_name}' implements an Abstract Factory producing concrete product families",
                            weight=0.80,
                            rule_code="GOF_ABSTRACT_FACTORY_CLASS",
                            location=cls.location,
                        )
                    ]
                    detections.append(self._create_detection(
                        target_name=f"{m.namespace}.{cls_name}",
                        target_kind="abstract_factory_class",
                        evidences=evidences,
                        location=cls.location,
                    ))
        return detections


class BuilderPatternRule(BasePatternRule):
    """Detects Builder Pattern: fluent builder class with Build() method and fluent return `this`."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.BUILDER_PATTERN

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            raw = m.raw_source
            for cls_name, cls in m.classes.items():
                is_builder_name = "Builder" in cls_name
                has_build_method = "Build(" in raw or "Create(" in raw or "return this;" in raw
                if is_builder_name and has_build_method:
                    evidences = [
                        Evidence(
                            description=f"Class '{cls_name}' implements Builder Pattern providing fluent method chaining and final `Build()` construction",
                            weight=0.90,
                            rule_code="GOF_BUILDER_PATTERN",
                            location=cls.location,
                        )
                    ]
                    detections.append(self._create_detection(
                        target_name=f"{m.namespace}.{cls_name}",
                        target_kind="builder_class",
                        evidences=evidences,
                        location=cls.location,
                    ))
        return detections


class FactoryMethodRule(BasePatternRule):
    """Detects Factory Method: static creation methods returning instances or Result wrappers."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.FACTORY_METHOD

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            raw = m.raw_source
            # Check for static factory methods: public static [Type] Create(...) or From(...)
            matches = re.findall(r"public\s+static\s+(?:async\s+)?([\w<>,]+)\s+(Create|From|Of|Parse|New)\s*\(", raw)
            if matches:
                for ret_type, method_name in matches:
                    evidences = [
                        Evidence(
                            description=f"Static Factory Method `{method_name}(...)` encapsulates creation and returns `{ret_type}`",
                            weight=0.85,
                            rule_code="GOF_FACTORY_METHOD",
                            location=m.location,
                        )
                    ]
                    detections.append(self._create_detection(
                        target_name=f"{m.namespace}.{m.name}.{method_name}",
                        target_kind="factory_method",
                        evidences=evidences,
                        location=m.location,
                    ))
        return detections


class PrototypeCloneRule(BasePatternRule):
    """Detects Prototype / Clone Pattern: ICloneable, Clone(), or record `with` copy."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.PROTOTYPE_CLONE

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            raw = m.raw_source
            for cls_name, cls in m.classes.items():
                is_cloneable_named = "Prototype" in cls_name
                is_cloneable_impl = "ICloneable" in cls.implements_list
                if is_cloneable_named or is_cloneable_impl:
                    evidences = [
                        Evidence(
                            description=f"Class '{cls_name}' implements Prototype pattern via `ICloneable` / `Clone()` method",
                            weight=0.85,
                            rule_code="GOF_PROTOTYPE_CLONEABLE",
                            location=cls.location,
                        )
                    ]
                    detections.append(self._create_detection(
                        target_name=f"{m.namespace}.{cls_name}",
                        target_kind="prototype_class",
                        evidences=evidences,
                        location=cls.location,
                    ))
            if " with {" in raw or " with { " in raw:
                evidences = [
                    Evidence(
                        description=f"Module '{m.name}' adopts non-destructive mutation (`with {{ ... }}`) Prototype cloning",
                        weight=0.80,
                        rule_code="CSHARP_RECORD_WITH_PROTOTYPE",
                        location=m.location,
                    )
                ]
                detections.append(self._create_detection(
                    target_name=f"{m.namespace}.{m.name}",
                    target_kind="prototype_record_mutation",
                    evidences=evidences,
                    location=m.location,
                ))
        return detections


class SingletonPatternRule(BasePatternRule):
    """Detects Singleton Pattern: Lazy<T>, private constructors with static instance property."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.SINGLETON_PATTERN

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            raw = m.raw_source
            for cls_name, cls in m.classes.items():
                has_lazy = f"Lazy<{cls_name}>" in raw
                has_instance_prop = "Instance" in raw and ("static" in raw or "public static" in raw)
                has_priv_ctor = f"private {cls_name}(" in raw
                if (has_lazy or (has_instance_prop and has_priv_ctor)) or "Singleton" in cls_name:
                    evidences = [
                        Evidence(
                            description=f"Class '{cls_name}' implements thread-safe Singleton Pattern using private constructor and static Instance accessor",
                            weight=0.90,
                            rule_code="GOF_SINGLETON_PATTERN",
                            location=cls.location,
                        )
                    ]
                    detections.append(self._create_detection(
                        target_name=f"{m.namespace}.{cls_name}",
                        target_kind="singleton_class",
                        evidences=evidences,
                        location=cls.location,
                    ))
        return detections
