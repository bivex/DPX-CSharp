"""Concurrency, Channels, and Task Parallel Library (TPL) Rules for C# / .NET."""

from __future__ import annotations

from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class ChannelProducerConsumerRule(BasePatternRule):
    """Detects `System.Threading.Channels` for lock-free producer-consumer concurrency."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.CHANNEL_PRODUCER_CONSUMER

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            raw = m.raw_source
            if "Channel.CreateBounded<" in raw or "Channel.CreateUnbounded<" in raw or "ChannelReader<" in raw:
                evidences = [
                    Evidence(
                        description=f"Module '{m.name}' coordinates asynchronous message flows via high-throughput `System.Threading.Channels`",
                        weight=0.90,
                        rule_code="NET_CHANNEL_PRODUCER_CONSUMER",
                        location=m.location,
                    )
                ]
                detections.append(self._create_detection(
                    target_name=f"{m.namespace}.{m.name}",
                    target_kind="channel_pipeline_module",
                    evidences=evidences,
                    location=m.location,
                ))
        return detections


class StructuredTaskWhenAllRule(BasePatternRule):
    """Detects Structured Concurrency via `Task.WhenAll()` or `Task.WhenAny()`."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.STRUCTURED_TASK_WHEN_ALL

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            raw = m.raw_source
            if "Task.WhenAll(" in raw or "Task.WhenAny(" in raw:
                evidences = [
                    Evidence(
                        description=f"Module '{m.name}' executes structured parallel asynchronous operations using `Task.WhenAll()` / `Task.WhenAny()`",
                        weight=0.85,
                        rule_code="NET_STRUCTURED_TASK_WHEN_ALL",
                        location=m.location,
                    )
                ]
                detections.append(self._create_detection(
                    target_name=f"{m.namespace}.{m.name}",
                    target_kind="structured_task_module",
                    evidences=evidences,
                    location=m.location,
                ))
        return detections


class AsyncLockSemaphoreRule(BasePatternRule):
    """Detects asynchronous locking using `SemaphoreSlim.WaitAsync()`."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.ASYNC_LOCK_SEMAPHORE

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            raw = m.raw_source
            if "SemaphoreSlim" in raw and "WaitAsync(" in raw:
                evidences = [
                    Evidence(
                        description=f"Module '{m.name}' performs non-blocking async mutual exclusion with `SemaphoreSlim.WaitAsync()`",
                        weight=0.90,
                        rule_code="NET_ASYNC_LOCK_SEMAPHORE",
                        location=m.location,
                    )
                ]
                detections.append(self._create_detection(
                    target_name=f"{m.namespace}.{m.name}",
                    target_kind="async_lock_module",
                    evidences=evidences,
                    location=m.location,
                ))
        return detections


class AsyncEnumerableStreamRule(BasePatternRule):
    """Detects asynchronous streaming using `IAsyncEnumerable<T>` and `await foreach`."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.ASYNC_ENUMERABLE_STREAM

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            raw = m.raw_source
            if "IAsyncEnumerable<" in raw or "await foreach " in raw:
                evidences = [
                    Evidence(
                        description=f"Module '{m.name}' produces or consumes asynchronous pull-based streams via `IAsyncEnumerable<T>`",
                        weight=0.90,
                        rule_code="NET_ASYNC_ENUMERABLE_STREAM",
                        location=m.location,
                    )
                ]
                detections.append(self._create_detection(
                    target_name=f"{m.namespace}.{m.name}",
                    target_kind="async_enumerable_module",
                    evidences=evidences,
                    location=m.location,
                ))
        return detections
