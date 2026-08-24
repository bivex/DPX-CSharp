"""Tests for resilience and hazard rules."""

from __future__ import annotations

from pattern_detector.adapters.outbound.parsers.native_cs_parser_adapter import NativeCSharpParserAdapter
from pattern_detector.domain.rules.resilience_rules import (
    IDisposableLeakHazardRule,
    MutableStaticFieldRule,
    NullForgivingSuppressionRule,
    SyncOverAsyncDeadlockRule,
    TryCatchBlanketSwallowRule,
)


def test_hazards_on_trading_engine():
    parser = NativeCSharpParserAdapter()
    model = parser.parse_project("examples/csharp_samples/TradingEngineHazards.cs")

    deadlocks = SyncOverAsyncDeadlockRule().detect(model)
    assert len(deadlocks) >= 1

    leaks = IDisposableLeakHazardRule().detect(model)
    assert len(leaks) >= 1

    null_suppress = NullForgivingSuppressionRule().detect(model)
    assert len(null_suppress) >= 1

    swallow = TryCatchBlanketSwallowRule().detect(model)
    assert len(swallow) >= 1

    mutable_static = MutableStaticFieldRule().detect(model)
    assert len(mutable_static) >= 1
