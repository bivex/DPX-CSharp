"""Enterprise & Modern .NET Architecture Rules for C#."""

from __future__ import annotations

import re
from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class CQRSMediatRRule(BasePatternRule):
    """Detects CQRS and MediatR handlers (`IRequestHandler<TRequest, TResponse>`, `IQueryHandler`, `ICommandHandler`)."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.CQRS_MEDIATR_HANDLER

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            for cls_name, cls in m.classes.items():
                is_mediatr = any("IRequestHandler<" in iface or "INotificationHandler<" in iface for iface in cls.implements_list)
                is_cqrs_name = "CommandHandler" in cls_name or "QueryHandler" in cls_name
                if is_mediatr or is_cqrs_name:
                    evidences = [
                        Evidence(
                            description=f"Class '{cls_name}' implements CQRS / MediatR Request Handler separating command execution from query reads",
                            weight=0.90,
                            rule_code="NET_CQRS_MEDIATR_HANDLER",
                            location=cls.location,
                        )
                    ]
                    detections.append(self._create_detection(
                        target_name=f"{m.namespace}.{cls_name}",
                        target_kind="cqrs_handler_class",
                        evidences=evidences,
                        location=cls.location,
                    ))
        return detections


class RepositoryUnitOfWorkRule(BasePatternRule):
    """Detects Repository and Unit of Work patterns (`IRepository<T>`, `IUnitOfWork`, `SaveChangesAsync()`)."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.REPOSITORY_UNIT_OF_WORK

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            for iface_name, iface in m.interfaces.items():
                if "Repository" in iface_name or "UnitOfWork" in iface_name:
                    evidences = [
                        Evidence(
                            description=f"Interface '{iface_name}' defines Repository / Unit of Work persistence abstraction decoupling domain from EF Core",
                            weight=0.90,
                            rule_code="NET_REPOSITORY_UNIT_OF_WORK_INTERFACE",
                            location=iface.location,
                        )
                    ]
                    detections.append(self._create_detection(
                        target_name=f"{m.namespace}.{iface_name}",
                        target_kind="repository_uow_interface",
                        evidences=evidences,
                        location=iface.location,
                    ))
            for cls_name, cls in m.classes.items():
                if "Repository" in cls_name or "UnitOfWork" in cls_name:
                    evidences = [
                        Evidence(
                            description=f"Class '{cls_name}' implements Repository / Unit of Work managing entity persistence lifecycle",
                            weight=0.85,
                            rule_code="NET_REPOSITORY_UNIT_OF_WORK_CLASS",
                            location=cls.location,
                        )
                    ]
                    detections.append(self._create_detection(
                        target_name=f"{m.namespace}.{cls_name}",
                        target_kind="repository_uow_class",
                        evidences=evidences,
                        location=cls.location,
                    ))
        return detections


class OptionsPatternConfigurationRule(BasePatternRule):
    """Detects .NET Options Pattern configuration (`IOptions<T>`, `IOptionsSnapshot<T>`, `IOptionsMonitor<T>`)."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.OPTIONS_PATTERN_CONFIGURATION

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            raw = m.raw_source
            for cls_name, cls in m.classes.items():
                has_options_param = any("IOptions<" in p or "IOptionsSnapshot<" in p or "IOptionsMonitor<" in p for p in cls.constructor_params)
                if has_options_param or "IOptions<" in raw:
                    evidences = [
                        Evidence(
                            description=f"Class '{cls_name}' binds strongly-typed settings using .NET Options Pattern (`IOptions<T>`)",
                            weight=0.90,
                            rule_code="NET_OPTIONS_PATTERN_CONFIGURATION",
                            location=cls.location,
                        )
                    ]
                    detections.append(self._create_detection(
                        target_name=f"{m.namespace}.{cls_name}",
                        target_kind="options_configured_class",
                        evidences=evidences,
                        location=cls.location,
                    ))
                    break
        return detections


class RailwayResultMonadRule(BasePatternRule):
    """Detects Railway-Oriented Result or ErrorOr monad types for type-safe error handling."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.RAILWAY_RESULT_MONAD

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            raw = m.raw_source
            has_result_return = "Result<" in raw or "ErrorOr<" in raw or "OneOf<" in raw or "Fin<" in raw
            if has_result_return:
                evidences = [
                    Evidence(
                        description=f"Module '{m.name}' adopts Railway-Oriented Programming (`Result<T, E>` / `ErrorOr<T>`) for total, exception-free error handling",
                        weight=0.90,
                        rule_code="NET_RAILWAY_RESULT_MONAD",
                        location=m.location,
                    )
                ]
                detections.append(self._create_detection(
                    target_name=f"{m.namespace}.{m.name}",
                    target_kind="railway_result_module",
                    evidences=evidences,
                    location=m.location,
                ))
        return detections


class DependencyInjectionServiceCollectionRule(BasePatternRule):
    """Detects .NET Dependency Injection registration (`IServiceCollection`, `AddScoped`, `AddTransient`, `AddSingleton`)."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.DEPENDENCY_INJECTION_SERVICE_COLLECTION

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            raw = m.raw_source
            has_di_methods = "AddScoped<" in raw or "AddTransient<" in raw or "AddSingleton<" in raw or "this IServiceCollection" in raw
            if has_di_methods:
                evidences = [
                    Evidence(
                        description=f"Module '{m.name}' configures IoC container bindings via `IServiceCollection` extension methods",
                        weight=0.90,
                        rule_code="NET_DEPENDENCY_INJECTION_REGISTRATION",
                        location=m.location,
                    )
                ]
                detections.append(self._create_detection(
                    target_name=f"{m.namespace}.{m.name}",
                    target_kind="di_service_collection_module",
                    evidences=evidences,
                    location=m.location,
                ))
        return detections
