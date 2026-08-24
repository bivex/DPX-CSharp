"""Tests for all GoF Creational, Structural, and Behavioral rules."""

from __future__ import annotations

from pattern_detector.adapters.outbound.parsers.native_cs_parser_adapter import NativeCSharpParserAdapter
from pattern_detector.domain.rules.creational_rules import (
    AbstractFactoryRule,
    BuilderPatternRule,
    FactoryMethodRule,
    PrototypeCloneRule,
    SingletonPatternRule,
)
from pattern_detector.domain.rules.structural_rules import (
    AdapterPatternRule,
    BridgePatternRule,
    CompositePatternRule,
    DecoratorPatternRule,
    FacadePatternRule,
    FlyweightPatternRule,
    ProxyHandlerRule,
)
from pattern_detector.domain.rules.behavioral_rules import (
    ChainOfResponsibilityRule,
    CommandPatternRule,
    InterpreterPatternRule,
    IteratorYieldRule,
    MediatorPatternRule,
    MementoPatternRule,
    ObserverEventObservableRule,
    StatePatternRule,
    StrategyPatternRule,
    TemplateMethodRule,
    VisitorPatternRule,
)


def test_gof_patterns_on_samples():
    parser = NativeCSharpParserAdapter()
    model = parser.parse_project("examples/csharp_samples/GoFPatterns.cs")

    # Creational (5/5)
    assert len(AbstractFactoryRule().detect(model)) >= 1
    assert len(BuilderPatternRule().detect(model)) >= 1
    assert len(FactoryMethodRule().detect(model)) >= 1
    assert len(PrototypeCloneRule().detect(model)) >= 1
    assert len(SingletonPatternRule().detect(model)) >= 1

    # Structural (7/7)
    assert len(AdapterPatternRule().detect(model)) >= 1
    assert len(BridgePatternRule().detect(model)) >= 1
    assert len(CompositePatternRule().detect(model)) >= 1
    assert len(DecoratorPatternRule().detect(model)) >= 1
    assert len(FacadePatternRule().detect(model)) >= 1
    assert len(FlyweightPatternRule().detect(model)) >= 1
    assert len(ProxyHandlerRule().detect(model)) >= 1

    # Behavioral (11/11)
    assert len(ChainOfResponsibilityRule().detect(model)) >= 1
    assert len(CommandPatternRule().detect(model)) >= 1
    assert len(InterpreterPatternRule().detect(model)) >= 1
    assert len(IteratorYieldRule().detect(model)) >= 1
    assert len(MediatorPatternRule().detect(model)) >= 1
    assert len(MementoPatternRule().detect(model)) >= 1
    assert len(ObserverEventObservableRule().detect(model)) >= 1
    assert len(StatePatternRule().detect(model)) >= 1
    assert len(StrategyPatternRule().detect(model)) >= 1
    assert len(TemplateMethodRule().detect(model)) >= 1
    assert len(VisitorPatternRule().detect(model)) >= 1
