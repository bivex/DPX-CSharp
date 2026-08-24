"""Domain Value Objects, Enums, and Core Models for C# / .NET Pattern Detector."""

from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class PatternCategory(str, Enum):
    """Architectural and Design Pattern Categories for C# / .NET."""

    TYPE_SYSTEM = "type_system"
    CREATIONAL = "creational"
    STRUCTURAL = "structural"
    BEHAVIORAL = "behavioral"
    ENTERPRISE = "enterprise"
    CONCURRENCY_ASYNC = "concurrency_async"
    RESILIENCE = "resilience"
    PRINCIPLE = "principle"


class PatternType(str, Enum):
    """46 C# / .NET Design Patterns, Modern Idioms & Code Hazards."""

    # 1. Type System, Records & Pattern Matching (5)
    RECORD_STRUCT_IMMUTABILITY = "record_struct_immutability"
    PATTERN_MATCHING_SWITCH = "pattern_matching_switch"
    PRIMARY_CONSTRUCTOR = "primary_constructor"
    GENERIC_VARIANCE_IN_OUT = "generic_variance_in_out"
    EXPRESSION_TREE_LINQ = "expression_tree_linq"

    # 2. Creational Patterns — Full GoF (5)
    ABSTRACT_FACTORY = "abstract_factory"
    BUILDER_PATTERN = "builder_pattern"
    FACTORY_METHOD = "factory_method"
    PROTOTYPE_CLONE = "prototype_clone"
    SINGLETON_PATTERN = "singleton_pattern"

    # 3. Structural Patterns — Full GoF (7)
    ADAPTER_PATTERN = "adapter_pattern"
    BRIDGE_PATTERN = "bridge_pattern"
    COMPOSITE_PATTERN = "composite_pattern"
    DECORATOR_PATTERN = "decorator_pattern"
    FACADE_PATTERN = "facade_pattern"
    FLYWEIGHT_PATTERN = "flyweight_pattern"
    PROXY_HANDLER = "proxy_handler"

    # 4. Behavioral Patterns — Full GoF (11)
    CHAIN_OF_RESPONSIBILITY = "chain_of_responsibility"
    COMMAND_PATTERN = "command_pattern"
    INTERPRETER_PATTERN = "interpreter_pattern"
    ITERATOR_YIELD = "iterator_yield"
    MEDIATOR_PATTERN = "mediator_pattern"
    MEMENTO_PATTERN = "memento_pattern"
    OBSERVER_EVENT_OBSERVABLE = "observer_event_observable"
    STATE_PATTERN = "state_pattern"
    STRATEGY_PATTERN = "strategy_pattern"
    TEMPLATE_METHOD = "template_method"
    VISITOR_PATTERN = "visitor_pattern"

    # 5. Enterprise & .NET Architecture (5)
    CQRS_MEDIATR_HANDLER = "cqrs_mediatr_handler"
    REPOSITORY_UNIT_OF_WORK = "repository_unit_of_work"
    OPTIONS_PATTERN_CONFIGURATION = "options_pattern_configuration"
    RAILWAY_RESULT_MONAD = "railway_result_monad"
    DEPENDENCY_INJECTION_SERVICE_COLLECTION = "dependency_injection_service_collection"

    # 6. Concurrency, Channels & TPL (4)
    CHANNEL_PRODUCER_CONSUMER = "channel_producer_consumer"
    STRUCTURED_TASK_WHEN_ALL = "structured_task_when_all"
    ASYNC_LOCK_SEMAPHORE = "async_lock_semaphore"
    ASYNC_ENUMERABLE_STREAM = "async_enumerable_stream"

    # 7. Resilience & Resource Safety (5)
    SYNC_OVER_ASYNC_DEADLOCK = "sync_over_async_deadlock"
    IDISPOSABLE_LEAK_HAZARD = "idisposable_leak_hazard"
    NULL_FORGIVING_SUPPRESSION = "null_forgiving_suppression"
    TRY_CATCH_BLANKET_SWALLOW = "try_catch_blanket_swallow"
    MUTABLE_STATIC_FIELD = "mutable_static_field"

    # 8. Principles, Complexity & Quality (4)
    GOD_CLASS_SRP = "god_class_srp"
    CYCLOMATIC_COMPLEXITY_KISS = "cyclomatic_complexity_kiss"
    DUPLICATE_CODE_DRY = "duplicate_code_dry"
    CIRCULAR_NAMESPACE_DEPENDENCY = "circular_namespace_dependency"


class ConfidenceLevel(str, Enum):
    """Confidence classification for static detections."""

    VERY_HIGH = "VERY_HIGH"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Location(BaseModel):
    """Exact source location of a detected pattern in a C# source file."""

    file_path: str
    start_line: int
    start_col: int = 1
    end_line: int | None = None
    end_col: int | None = None

    def __str__(self) -> str:
        if self.end_line and self.end_line != self.start_line:
            return f"{self.file_path}:{self.start_line}-{self.end_line}:{self.start_col}"
        return f"{self.file_path}:{self.start_line}:{self.start_col}"


class Evidence(BaseModel):
    """Individual heuristic evidence trail supporting a pattern detection."""

    description: str
    weight: float = Field(default=0.8, ge=0.0, le=1.0)
    rule_code: str
    location: Location | None = None


class Confidence(BaseModel):
    """Aggregated numerical confidence score with classification level."""

    value: float = Field(ge=0.0, le=1.0)

    @property
    def level(self) -> ConfidenceLevel:
        if self.value >= 0.85:
            return ConfidenceLevel.VERY_HIGH
        if self.value >= 0.70:
            return ConfidenceLevel.HIGH
        if self.value >= 0.50:
            return ConfidenceLevel.MEDIUM
        return ConfidenceLevel.LOW

    @property
    def percentage_str(self) -> str:
        return f"{int(round(self.value * 100))}%"
