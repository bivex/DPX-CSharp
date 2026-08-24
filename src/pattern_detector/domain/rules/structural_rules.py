"""Structural GoF Design Pattern Rules for C# / .NET."""

from __future__ import annotations

import re
from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class AdapterPatternRule(BasePatternRule):
    """Detects Adapter Pattern: class wrapping an adaptee instance to conform to a target interface."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.ADAPTER_PATTERN

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            for cls_name, cls in m.classes.items():
                if "Adapter" in cls_name and cls.implements_list:
                    evidences = [
                        Evidence(
                            description=f"Class '{cls_name}' implements Adapter Pattern adapting an external dependency to interface '{cls.implements_list[0]}'",
                            weight=0.90,
                            rule_code="GOF_ADAPTER_PATTERN",
                            location=cls.location,
                        )
                    ]
                    detections.append(self._create_detection(
                        target_name=f"{m.namespace}.{cls_name}",
                        target_kind="adapter_class",
                        evidences=evidences,
                        location=cls.location,
                    ))
        return detections


class BridgePatternRule(BasePatternRule):
    """Detects Bridge Pattern: abstract class composing an Implementor interface via constructor."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.BRIDGE_PATTERN

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        bridge_kw = {"Device", "Renderer", "Implementor", "Backend", "Driver", "Engine", "Platform"}
        for m in model.all_modules():
            for cls_name, cls in m.classes.items():
                if (cls.is_abstract or "Bridge" in cls_name) and cls.constructor_params:
                    for param in cls.constructor_params:
                        if any(kw in param for kw in bridge_kw):
                            evidences = [
                                Evidence(
                                    description=f"Class '{cls_name}' composes implementor dependency `{param}` — Bridge Pattern decoupling abstraction from implementation",
                                    weight=0.85,
                                    rule_code="GOF_BRIDGE_PATTERN",
                                    location=cls.location,
                                )
                            ]
                            detections.append(self._create_detection(
                                target_name=f"{m.namespace}.{cls_name}",
                                target_kind="bridge_class",
                                evidences=evidences,
                                location=cls.location,
                            ))
                            break
        return detections


class CompositePatternRule(BasePatternRule):
    """Detects Composite Pattern: recursive tree structures with children collections of same interface."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.COMPOSITE_PATTERN

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            raw = m.raw_source
            for cls_name, cls in m.classes.items():
                is_composite_name = "Composite" in cls_name
                # Check if this specific class has a children collection
                class_chunk_match = re.search(rf"class\s+{cls_name}[^{{]*\{{([^}}]+)\}}", raw, re.DOTALL)
                class_body = class_chunk_match.group(1) if class_chunk_match else ""
                has_children = bool(re.search(r"(?:List|IList|ICollection|IEnumerable|HashSet)<[^>]+>[\s\w]*_?(?:children|nodes|items|elements)", class_body, re.IGNORECASE))
                if is_composite_name or (has_children and ("Add" in class_body or "Remove" in class_body)):
                    evidences = [
                        Evidence(
                            description=f"Class '{cls_name}' represents a Composite tree node managing a recursive collection of children",
                            weight=0.85,
                            rule_code="GOF_COMPOSITE_TREE_STRUCTURE",
                            location=cls.location,
                        )
                    ]
                    detections.append(self._create_detection(
                        target_name=f"{m.namespace}.{cls_name}",
                        target_kind="composite_class",
                        evidences=evidences,
                        location=cls.location,
                    ))
        return detections


class DecoratorPatternRule(BasePatternRule):
    """Detects Decorator Pattern: class implementing an interface while wrapping an inner instance of the same interface."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.DECORATOR_PATTERN

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            for cls_name, cls in m.classes.items():
                if "Decorator" in cls_name or "Cached" in cls_name or "Logging" in cls_name:
                    if cls.implements_list:
                        target_iface = cls.implements_list[0]
                        # Check if constructor takes the same interface
                        if any(target_iface in p for p in cls.constructor_params) or "inner" in m.raw_source.lower():
                            evidences = [
                                Evidence(
                                    description=f"Class '{cls_name}' decorates interface '{target_iface}' by wrapping an inner instance with additional cross-cutting behavior",
                                    weight=0.90,
                                    rule_code="GOF_DECORATOR_PATTERN",
                                    location=cls.location,
                                )
                            ]
                            detections.append(self._create_detection(
                                target_name=f"{m.namespace}.{cls_name}",
                                target_kind="decorator_class",
                                evidences=evidences,
                                location=cls.location,
                            ))
        return detections


class FacadePatternRule(BasePatternRule):
    """Detects Facade Pattern: unified simplified class encapsulating multiple subsystem dependencies."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.FACADE_PATTERN

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            for cls_name, cls in m.classes.items():
                if "Facade" in cls_name or (len(cls.constructor_params) >= 3 and "Service" in cls_name and not cls.is_abstract):
                    evidences = [
                        Evidence(
                            description=f"Class '{cls_name}' coordinates {len(cls.constructor_params)} subsystem services as a simplified Facade",
                            weight=0.80,
                            rule_code="GOF_FACADE_PATTERN",
                            location=cls.location,
                        )
                    ]
                    detections.append(self._create_detection(
                        target_name=f"{m.namespace}.{cls_name}",
                        target_kind="facade_class",
                        evidences=evidences,
                        location=cls.location,
                    ))
        return detections


class FlyweightPatternRule(BasePatternRule):
    """Detects Flyweight Pattern: object pool or ConcurrentDictionary cache sharing immutable instances."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.FLYWEIGHT_PATTERN

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            raw = m.raw_source
            has_concurrent_cache = "ConcurrentDictionary<" in raw or "ArrayPool<" in raw or "ObjectPool<" in raw
            if has_concurrent_cache:
                for cls_name, cls in m.classes.items():
                    if "Pool" in cls_name or "Cache" in cls_name or "Flyweight" in cls_name or "Factory" in cls_name:
                        evidences = [
                            Evidence(
                                description=f"Class '{cls_name}' manages a Flyweight / Object Pool cache sharing fine-grained reusable instances",
                                weight=0.85,
                                rule_code="GOF_FLYWEIGHT_OBJECT_POOL",
                                location=cls.location,
                            )
                        ]
                        detections.append(self._create_detection(
                            target_name=f"{m.namespace}.{cls_name}",
                            target_kind="flyweight_pool_class",
                            evidences=evidences,
                            location=cls.location,
                        ))
        return detections


class ProxyHandlerRule(BasePatternRule):
    """Detects Proxy Pattern: surrogate class controlling access to a real subject."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.PROXY_HANDLER

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            for cls_name, cls in m.classes.items():
                if "Proxy" in cls_name and cls.implements_list:
                    evidences = [
                        Evidence(
                            description=f"Class '{cls_name}' acts as a Proxy for interface '{cls.implements_list[0]}'",
                            weight=0.85,
                            rule_code="GOF_PROXY_PATTERN",
                            location=cls.location,
                        )
                    ]
                    detections.append(self._create_detection(
                        target_name=f"{m.namespace}.{cls_name}",
                        target_kind="proxy_class",
                        evidences=evidences,
                        location=cls.location,
                    ))
        return detections
