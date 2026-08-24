"""Tests for C# native parser adapter."""

from __future__ import annotations

from pattern_detector.adapters.outbound.parsers.native_cs_parser_adapter import NativeCSharpParserAdapter


def test_parse_project_samples():
    parser = NativeCSharpParserAdapter()
    model = parser.parse_project("examples/csharp_samples")
    assert model.total_modules >= 3


def test_parse_records():
    parser = NativeCSharpParserAdapter()
    model = parser.parse_project("examples/csharp_samples")
    all_records = {}
    for m in model.all_modules():
        all_records.update(m.records)

    assert "Money" in all_records
    assert all_records["Money"].is_readonly
    assert all_records["Money"].is_struct


def test_parse_classes_and_primary_constructors():
    parser = NativeCSharpParserAdapter()
    model = parser.parse_project("examples/csharp_samples")
    all_classes = {}
    for m in model.all_modules():
        all_classes.update(m.classes)

    assert "Account" in all_classes
    assert all_classes["Account"].has_primary_constructor
    assert len(all_classes["Account"].constructor_params) == 3


def test_parse_interfaces():
    parser = NativeCSharpParserAdapter()
    model = parser.parse_project("examples/csharp_samples")
    all_ifaces = {}
    for m in model.all_modules():
        all_ifaces.update(m.interfaces)

    assert "IReadOnlyRepository" in all_ifaces
    assert all_ifaces["IReadOnlyRepository"].has_in_out_variance
