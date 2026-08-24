"""Tests for Type System, Records, and Pattern Matching rules."""

from __future__ import annotations

from pattern_detector.domain.code_model import CSClass, CSInterface, CSModule, CSRecord, CodeModel
from pattern_detector.domain.rules.type_system_rules import (
    GenericVarianceInOutRule,
    PatternMatchingSwitchRule,
    PrimaryConstructorRule,
    RecordStructImmutabilityRule,
)


def test_record_struct_detection():
    model = CodeModel()
    m = CSModule(path="Money.cs", namespace="App.Domain")
    m.records["Money"] = CSRecord(name="Money", is_readonly=True, is_struct=True)
    model.add_module(m)

    results = RecordStructImmutabilityRule().detect(model)
    assert len(results) == 1
    assert "App.Domain.Money" in results[0].target_name


def test_primary_constructor_detection():
    model = CodeModel()
    m = CSModule(path="Service.cs", namespace="App.Services")
    m.classes["UserService"] = CSClass(
        name="UserService",
        has_primary_constructor=True,
        constructor_params=["IUserRepository repo", "ILogger logger"],
    )
    model.add_module(m)

    results = PrimaryConstructorRule().detect(model)
    assert len(results) == 1
    assert "App.Services.UserService" in results[0].target_name


def test_generic_variance_detection():
    model = CodeModel()
    m = CSModule(path="IRepo.cs", namespace="App.Domain")
    m.interfaces["IReadOnlyRepository"] = CSInterface(
        name="IReadOnlyRepository",
        is_generic=True,
        has_in_out_variance=True,
    )
    model.add_module(m)

    results = GenericVarianceInOutRule().detect(model)
    assert len(results) == 1
