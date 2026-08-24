"""Tests for Enterprise & .NET architecture rules."""

from __future__ import annotations

from pattern_detector.adapters.outbound.parsers.native_cs_parser_adapter import NativeCSharpParserAdapter
from pattern_detector.domain.rules.enterprise_rules import (
    CQRSMediatRRule,
    OptionsPatternConfigurationRule,
    RailwayResultMonadRule,
    RepositoryUnitOfWorkRule,
)


def test_enterprise_rules_on_banking_domain():
    parser = NativeCSharpParserAdapter()
    model = parser.parse_project("examples/csharp_samples/BankingDomain.cs")

    cqrs_detections = CQRSMediatRRule().detect(model)
    assert len(cqrs_detections) >= 1

    repo_detections = RepositoryUnitOfWorkRule().detect(model)
    assert len(repo_detections) >= 1

    options_detections = OptionsPatternConfigurationRule().detect(model)
    assert len(options_detections) >= 1

    result_detections = RailwayResultMonadRule().detect(model)
    assert len(result_detections) >= 1
