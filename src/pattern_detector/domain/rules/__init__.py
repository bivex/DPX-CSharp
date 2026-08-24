"""Rule catalog registration for C# / .NET Pattern Detector (46 Rules)."""

from __future__ import annotations

from pattern_detector.domain.rules.base import BasePatternRule, PatternRule
from pattern_detector.domain.rules.type_system_rules import (
    ExpressionTreeLinqRule,
    GenericVarianceInOutRule,
    PatternMatchingSwitchRule,
    PrimaryConstructorRule,
    RecordStructImmutabilityRule,
)
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
from pattern_detector.domain.rules.enterprise_rules import (
    CQRSMediatRRule,
    DependencyInjectionServiceCollectionRule,
    OptionsPatternConfigurationRule,
    RailwayResultMonadRule,
    RepositoryUnitOfWorkRule,
)
from pattern_detector.domain.rules.concurrency_rules import (
    AsyncEnumerableStreamRule,
    AsyncLockSemaphoreRule,
    ChannelProducerConsumerRule,
    StructuredTaskWhenAllRule,
)
from pattern_detector.domain.rules.resilience_rules import (
    IDisposableLeakHazardRule,
    MutableStaticFieldRule,
    NullForgivingSuppressionRule,
    SyncOverAsyncDeadlockRule,
    TryCatchBlanketSwallowRule,
)
from pattern_detector.domain.rules.quality_rules import (
    CircularNamespaceDependencyRule,
    CyclomaticComplexityKissRule,
    DuplicateCodeDryRule,
    GodClassSrpRule,
)

DEFAULT_RULES: list[PatternRule] = [
    # 1. Type System, Records & Pattern Matching (5)
    RecordStructImmutabilityRule(),
    PatternMatchingSwitchRule(),
    PrimaryConstructorRule(),
    GenericVarianceInOutRule(),
    ExpressionTreeLinqRule(),

    # 2. Creational Patterns — Full GoF (5)
    AbstractFactoryRule(),
    BuilderPatternRule(),
    FactoryMethodRule(),
    PrototypeCloneRule(),
    SingletonPatternRule(),

    # 3. Structural Patterns — Full GoF (7)
    AdapterPatternRule(),
    BridgePatternRule(),
    CompositePatternRule(),
    DecoratorPatternRule(),
    FacadePatternRule(),
    FlyweightPatternRule(),
    ProxyHandlerRule(),

    # 4. Behavioral Patterns — Full GoF (11)
    ChainOfResponsibilityRule(),
    CommandPatternRule(),
    InterpreterPatternRule(),
    IteratorYieldRule(),
    MediatorPatternRule(),
    MementoPatternRule(),
    ObserverEventObservableRule(),
    StatePatternRule(),
    StrategyPatternRule(),
    TemplateMethodRule(),
    VisitorPatternRule(),

    # 5. Enterprise & .NET Architecture (5)
    CQRSMediatRRule(),
    RepositoryUnitOfWorkRule(),
    OptionsPatternConfigurationRule(),
    RailwayResultMonadRule(),
    DependencyInjectionServiceCollectionRule(),

    # 6. Concurrency, Channels & TPL (4)
    ChannelProducerConsumerRule(),
    StructuredTaskWhenAllRule(),
    AsyncLockSemaphoreRule(),
    AsyncEnumerableStreamRule(),

    # 7. Resilience & Resource Safety (5)
    SyncOverAsyncDeadlockRule(),
    IDisposableLeakHazardRule(),
    NullForgivingSuppressionRule(),
    TryCatchBlanketSwallowRule(),
    MutableStaticFieldRule(),

    # 8. Principles, Complexity & Quality (4)
    GodClassSrpRule(),
    CyclomaticComplexityKissRule(),
    DuplicateCodeDryRule(),
    CircularNamespaceDependencyRule(),
]

__all__ = [
    "BasePatternRule",
    "PatternRule",
    "DEFAULT_RULES",
    # Type system
    "RecordStructImmutabilityRule", "PatternMatchingSwitchRule",
    "PrimaryConstructorRule", "GenericVarianceInOutRule", "ExpressionTreeLinqRule",
    # Creational
    "AbstractFactoryRule", "BuilderPatternRule", "FactoryMethodRule",
    "PrototypeCloneRule", "SingletonPatternRule",
    # Structural
    "AdapterPatternRule", "BridgePatternRule", "CompositePatternRule",
    "DecoratorPatternRule", "FacadePatternRule", "FlyweightPatternRule", "ProxyHandlerRule",
    # Behavioral
    "ChainOfResponsibilityRule", "CommandPatternRule", "InterpreterPatternRule",
    "IteratorYieldRule", "MediatorPatternRule", "MementoPatternRule",
    "ObserverEventObservableRule", "StatePatternRule", "StrategyPatternRule",
    "TemplateMethodRule", "VisitorPatternRule",
    # Enterprise
    "CQRSMediatRRule", "RepositoryUnitOfWorkRule", "OptionsPatternConfigurationRule",
    "RailwayResultMonadRule", "DependencyInjectionServiceCollectionRule",
    # Concurrency
    "ChannelProducerConsumerRule", "StructuredTaskWhenAllRule",
    "AsyncLockSemaphoreRule", "AsyncEnumerableStreamRule",
    # Resilience
    "SyncOverAsyncDeadlockRule", "IDisposableLeakHazardRule",
    "NullForgivingSuppressionRule", "TryCatchBlanketSwallowRule", "MutableStaticFieldRule",
    # Quality
    "GodClassSrpRule", "CyclomaticComplexityKissRule",
    "DuplicateCodeDryRule", "CircularNamespaceDependencyRule",
]
