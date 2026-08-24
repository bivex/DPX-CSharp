"""Behavioral GoF Design Pattern Rules for C# / .NET."""

from __future__ import annotations

import re
from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class ChainOfResponsibilityRule(BasePatternRule):
    """Detects Chain of Responsibility / ASP.NET Core Middleware pipeline (`RequestDelegate next`)."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.CHAIN_OF_RESPONSIBILITY

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            raw = m.raw_source
            # Middleware or handler chain: RequestDelegate next or IMiddleware or SetNext
            has_mw = "RequestDelegate " in raw or "IMiddleware" in raw or "await next(" in raw or "SetNext(" in raw
            if has_mw:
                for cls_name, cls in m.classes.items():
                    if "Middleware" in cls_name or "Handler" in cls_name:
                        evidences = [
                            Evidence(
                                description=f"Class '{cls_name}' processes requests in a Chain of Responsibility / Middleware Pipeline",
                                weight=0.90,
                                rule_code="GOF_CHAIN_OF_RESPONSIBILITY_MIDDLEWARE",
                                location=cls.location,
                            )
                        ]
                        detections.append(self._create_detection(
                            target_name=f"{m.namespace}.{cls_name}",
                            target_kind="middleware_chain_class",
                            evidences=evidences,
                            location=cls.location,
                        ))
        return detections


class CommandPatternRule(BasePatternRule):
    """Detects Command Pattern: classes or records encapsulating executable actions (`IRequest`, `ICommand`, `Execute()`)."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.COMMAND_PATTERN

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            for rec_name, rec in m.records.items():
                if "Command" in rec_name:
                    evidences = [
                        Evidence(
                            description=f"Record '{rec_name}' defines an immutable Command object carrying transactional intent",
                            weight=0.85,
                            rule_code="GOF_COMMAND_RECORD",
                            location=rec.location,
                        )
                    ]
                    detections.append(self._create_detection(
                        target_name=f"{m.namespace}.{rec_name}",
                        target_kind="command_record",
                        evidences=evidences,
                        location=rec.location,
                    ))
            for cls_name, cls in m.classes.items():
                if "Command" in cls_name and not "Handler" in cls_name:
                    evidences = [
                        Evidence(
                            description=f"Class '{cls_name}' encapsulates executable business logic in Command Pattern",
                            weight=0.80,
                            rule_code="GOF_COMMAND_CLASS",
                            location=cls.location,
                        )
                    ]
                    detections.append(self._create_detection(
                        target_name=f"{m.namespace}.{cls_name}",
                        target_kind="command_class",
                        evidences=evidences,
                        location=cls.location,
                    ))
        return detections


class InterpreterPatternRule(BasePatternRule):
    """Detects Interpreter Pattern: expression AST classes with `Interpret(Context)` method."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.INTERPRETER_PATTERN

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            raw = m.raw_source
            for iface_name, iface in m.interfaces.items():
                if any(mth.lower() in ("interpret", "evaluate", "eval") for mth in iface.methods) or "Expression" in iface_name:
                    evidences = [
                        Evidence(
                            description=f"Interface '{iface_name}' defines an AST grammar interpretation contract (`Interpret`)",
                            weight=0.85,
                            rule_code="GOF_INTERPRETER_INTERFACE",
                            location=iface.location,
                        )
                    ]
                    detections.append(self._create_detection(
                        target_name=f"{m.namespace}.{iface_name}",
                        target_kind="interpreter_interface",
                        evidences=evidences,
                        location=iface.location,
                    ))
            for cls_name, cls in m.classes.items():
                if "Expression" in cls_name and ("Interpret(" in raw or "Evaluate(" in raw):
                    evidences = [
                        Evidence(
                            description=f"Class '{cls_name}' models an AST Expression node with interpretation semantics",
                            weight=0.85,
                            rule_code="GOF_INTERPRETER_CLASS",
                            location=cls.location,
                        )
                    ]
                    detections.append(self._create_detection(
                        target_name=f"{m.namespace}.{cls_name}",
                        target_kind="interpreter_class",
                        evidences=evidences,
                        location=cls.location,
                    ))
        return detections


class IteratorYieldRule(BasePatternRule):
    """Detects Iterator Pattern & Generator via `yield return` or `yield break`."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.ITERATOR_YIELD

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            raw = m.raw_source
            if "yield return " in raw or "yield break;" in raw:
                evidences = [
                    Evidence(
                        description=f"Module '{m.name}' implements lazy sequence generator using compiler-synthesized `yield return` Iterator state machine",
                        weight=0.90,
                        rule_code="GOF_ITERATOR_YIELD_GENERATOR",
                        location=m.location,
                    )
                ]
                detections.append(self._create_detection(
                    target_name=f"{m.namespace}.{m.name}",
                    target_kind="yield_iterator_module",
                    evidences=evidences,
                    location=m.location,
                ))
        return detections


class MediatorPatternRule(BasePatternRule):
    """Detects Mediator Pattern: in-process bus or MediatR mediator dispatching commands/events."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.MEDIATOR_PATTERN

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            raw = m.raw_source
            for cls_name, cls in m.classes.items():
                has_mediator_dep = any("IMediator" in p or "ISender" in p or "IPublisher" in p for p in cls.constructor_params)
                is_mediator_class = "Mediator" in cls_name or "EventBus" in cls_name
                if has_mediator_dep or is_mediator_class:
                    evidences = [
                        Evidence(
                            description=f"Class '{cls_name}' coordinates operations via central in-process Mediator (`IMediator`)",
                            weight=0.85,
                            rule_code="GOF_MEDIATOR_PATTERN",
                            location=cls.location,
                        )
                    ]
                    detections.append(self._create_detection(
                        target_name=f"{m.namespace}.{cls_name}",
                        target_kind="mediator_dependent_class",
                        evidences=evidences,
                        location=cls.location,
                    ))
        return detections


class MementoPatternRule(BasePatternRule):
    """Detects Memento Pattern: state snapshot classes and undo/redo stacks."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.MEMENTO_PATTERN

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            raw = m.raw_source
            for cls_name, cls in m.classes.items():
                if "Memento" in cls_name or "Snapshot" in cls_name or "StateHistory" in cls_name:
                    evidences = [
                        Evidence(
                            description=f"Class '{cls_name}' captures immutable state snapshot for Memento / Undo rollback pattern",
                            weight=0.85,
                            rule_code="GOF_MEMENTO_SNAPSHOT",
                            location=cls.location,
                        )
                    ]
                    detections.append(self._create_detection(
                        target_name=f"{m.namespace}.{cls_name}",
                        target_kind="memento_class",
                        evidences=evidences,
                        location=cls.location,
                    ))
        return detections


class ObserverEventObservableRule(BasePatternRule):
    """Detects Observer Pattern: native `event EventHandler<T>`, `IObservable<T>`, or `IObserver<T>`."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.OBSERVER_EVENT_OBSERVABLE

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            raw = m.raw_source
            has_events = "event EventHandler" in raw or "event Action" in raw or "IObservable<" in raw
            if has_events:
                evidences = [
                    Evidence(
                        description=f"Module '{m.name}' publishes notifications using native C# `event EventHandler<T>` or `IObservable<T>` Observer pattern",
                        weight=0.90,
                        rule_code="GOF_OBSERVER_EVENT_OBSERVABLE",
                        location=m.location,
                    )
                ]
                detections.append(self._create_detection(
                    target_name=f"{m.namespace}.{m.name}",
                    target_kind="observer_event_module",
                    evidences=evidences,
                    location=m.location,
                ))
        return detections


class StatePatternRule(BasePatternRule):
    """Detects State Pattern: state objects or explicit finite state machine transitions."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.STATE_PATTERN

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            for cls_name, cls in m.classes.items():
                if "State" in cls_name and (cls.implements_list or cls.extends_name):
                    evidences = [
                        Evidence(
                            description=f"Class '{cls_name}' models a concrete State in a State Machine pattern",
                            weight=0.80,
                            rule_code="GOF_STATE_PATTERN_CLASS",
                            location=cls.location,
                        )
                    ]
                    detections.append(self._create_detection(
                        target_name=f"{m.namespace}.{cls_name}",
                        target_kind="state_class",
                        evidences=evidences,
                        location=cls.location,
                    ))
        return detections


class StrategyPatternRule(BasePatternRule):
    """Detects Strategy Pattern: pluggable algorithmic strategy interfaces and implementations."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.STRATEGY_PATTERN

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            for iface_name, iface in m.interfaces.items():
                if "Strategy" in iface_name or "Policy" in iface_name or "Algorithm" in iface_name:
                    evidences = [
                        Evidence(
                            description=f"Interface '{iface_name}' defines Strategy contract for pluggable algorithms",
                            weight=0.85,
                            rule_code="GOF_STRATEGY_INTERFACE",
                            location=iface.location,
                        )
                    ]
                    detections.append(self._create_detection(
                        target_name=f"{m.namespace}.{iface_name}",
                        target_kind="strategy_interface",
                        evidences=evidences,
                        location=iface.location,
                    ))
            for cls_name, cls in m.classes.items():
                if "Strategy" in cls_name and cls.implements_list:
                    evidences = [
                        Evidence(
                            description=f"Class '{cls_name}' provides concrete algorithmic Strategy implementation",
                            weight=0.85,
                            rule_code="GOF_STRATEGY_CLASS",
                            location=cls.location,
                        )
                    ]
                    detections.append(self._create_detection(
                        target_name=f"{m.namespace}.{cls_name}",
                        target_kind="strategy_class",
                        evidences=evidences,
                        location=cls.location,
                    ))
        return detections


class TemplateMethodRule(BasePatternRule):
    """Detects Template Method: abstract class with concrete template method calling abstract/virtual hooks."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.TEMPLATE_METHOD

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            raw = m.raw_source
            for cls_name, cls in m.classes.items():
                if cls.is_abstract and raw.count("abstract ") >= 2:
                    evidences = [
                        Evidence(
                            description=f"Abstract class '{cls_name}' defines skeleton algorithm with abstract hook methods — Template Method pattern",
                            weight=0.85,
                            rule_code="GOF_TEMPLATE_METHOD_PATTERN",
                            location=cls.location,
                        )
                    ]
                    detections.append(self._create_detection(
                        target_name=f"{m.namespace}.{cls_name}",
                        target_kind="template_method_class",
                        evidences=evidences,
                        location=cls.location,
                    ))
        return detections


class VisitorPatternRule(BasePatternRule):
    """Detects Visitor Pattern: visitor interfaces with `Visit(T)` and elements with `Accept(IVisitor)`."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.VISITOR_PATTERN

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            raw = m.raw_source
            for iface_name, iface in m.interfaces.items():
                visit_methods = [mth for mth in iface.methods if mth.startswith("Visit")]
                if len(visit_methods) >= 1 or "Visitor" in iface_name:
                    evidences = [
                        Evidence(
                            description=f"Interface '{iface_name}' declares Visitor double-dispatch contract (`Visit`)",
                            weight=0.90,
                            rule_code="GOF_VISITOR_INTERFACE",
                            location=iface.location,
                        )
                    ]
                    detections.append(self._create_detection(
                        target_name=f"{m.namespace}.{iface_name}",
                        target_kind="visitor_interface",
                        evidences=evidences,
                        location=iface.location,
                    ))
            if "Accept(I" in raw or ".Accept(" in raw:
                evidences = [
                    Evidence(
                        description=f"Module '{m.name}' implements `Accept(IVisitor)` dispatch for Visitor Pattern",
                        weight=0.85,
                        rule_code="GOF_VISITOR_ACCEPT_ELEMENT",
                        location=m.location,
                    )
                ]
                detections.append(self._create_detection(
                    target_name=f"{m.namespace}.{m.name}",
                    target_kind="visitor_element_module",
                    evidences=evidences,
                    location=m.location,
                ))
        return detections
