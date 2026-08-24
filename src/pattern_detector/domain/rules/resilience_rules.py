"""Resilience, Type Safety Hazards, and Resource Safety Rules for C# / .NET."""

from __future__ import annotations

import re
from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, Location, PatternType


class SyncOverAsyncDeadlockRule(BasePatternRule):
    """Detects Sync-over-Async blocking calls (`.Result`, `.Wait()`, `.GetAwaiter().GetResult()`)."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.SYNC_OVER_ASYNC_DEADLOCK

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        sync_pattern = re.compile(r"(\w+(?:\(\))?)\.(?:Result|Wait\(\)|GetAwaiter\(\)\.GetResult\(\))")
        for m in model.all_modules():
            for i, line in enumerate(m.raw_source.splitlines(), 1):
                if line.strip().startswith("//"):
                    continue
                match = sync_pattern.search(line)
                if match and "Task.WaitAll" not in line:
                    evidences = [
                        Evidence(
                            description=f"Blocking async call `{match.group(0)}` induces Sync-over-Async thread-pool starvation and potential deadlock",
                            weight=0.90,
                            rule_code="HAZARD_SYNC_OVER_ASYNC_DEADLOCK",
                            location=Location(file_path=m.path, start_line=i),
                        )
                    ]
                    detections.append(self._create_detection(
                        target_name=f"{m.namespace}.{m.name}:L{i}",
                        target_kind="sync_over_async_hazard",
                        evidences=evidences,
                        location=Location(file_path=m.path, start_line=i),
                    ))
        return detections


class IDisposableLeakHazardRule(BasePatternRule):
    """Detects disposable resource instantiation without `using` statement or `using var` declaration."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.IDISPOSABLE_LEAK_HAZARD

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        # Checks: new HttpClient(), new FileStream(), new SqlConnection() without preceding using
        leak_pattern = re.compile(r"^\s*(?:var|\w+)\s+\w+\s*=\s*new\s+(?:FileStream|MemoryStream|SqlConnection|HttpClient|StreamReader|StreamWriter)\s*\(", re.MULTILINE)
        for m in model.all_modules():
            for i, line in enumerate(m.raw_source.splitlines(), 1):
                if "using " not in line and leak_pattern.search(line):
                    evidences = [
                        Evidence(
                            description=f"Instantiation of IDisposable resource without `using` scope risks unmanaged handle / connection leaks",
                            weight=0.85,
                            rule_code="HAZARD_IDISPOSABLE_UNMANAGED_LEAK",
                            location=Location(file_path=m.path, start_line=i),
                        )
                    ]
                    detections.append(self._create_detection(
                        target_name=f"{m.namespace}.{m.name}:L{i}",
                        target_kind="idisposable_leak_hazard",
                        evidences=evidences,
                        location=Location(file_path=m.path, start_line=i),
                    ))
        return detections


class NullForgivingSuppressionRule(BasePatternRule):
    """Detects unchecked null-forgiving operator `!` bypassing compiler nullability checks."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.NULL_FORGIVING_SUPPRESSION

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        suppress_pattern = re.compile(r"(\w+)![\.;\)]")
        for m in model.all_modules():
            for i, line in enumerate(m.raw_source.splitlines(), 1):
                if line.strip().startswith("//"):
                    continue
                match = suppress_pattern.search(line)
                if match and "!=" not in line:
                    evidences = [
                        Evidence(
                            description=f"Null-forgiving operator `{match.group(0)}` forcefully silences compiler null-safety warnings, risking runtime NullReferenceException",
                            weight=0.80,
                            rule_code="HAZARD_NULL_FORGIVING_SUPPRESSION",
                            location=Location(file_path=m.path, start_line=i),
                        )
                    ]
                    detections.append(self._create_detection(
                        target_name=f"{m.namespace}.{m.name}:L{i}",
                        target_kind="null_forgiving_suppression",
                        evidences=evidences,
                        location=Location(file_path=m.path, start_line=i),
                    ))
        return detections


class TryCatchBlanketSwallowRule(BasePatternRule):
    """Detects empty or silent catch blocks catching base Exception."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.TRY_CATCH_BLANKET_SWALLOW

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        for m in model.all_modules():
            raw = m.raw_source
            for match in re.finditer(r"\bcatch(?:\s*\([^)]*\))?\s*\{", raw):
                start_idx = match.end()
                close_idx = raw.find("}", start_idx)
                if close_idx != -1 and (close_idx - start_idx) < 150:
                    body = raw[start_idx:close_idx].strip()
                    body_lines = [l.strip() for l in body.splitlines() if l.strip()]
                    if not body_lines or all(l.startswith("//") or l.startswith("/*") or l.startswith("*") for l in body_lines):
                        line_no = raw[:match.start()].count("\n") + 1
                        evidences = [
                            Evidence(
                                description="Blanket `catch` block swallows errors without logging or remediation",
                                weight=0.90,
                                rule_code="HAZARD_TRY_CATCH_BLANKET_SWALLOW",
                                location=Location(file_path=m.path, start_line=line_no),
                            )
                        ]
                        detections.append(self._create_detection(
                            target_name=f"{m.namespace}.{m.name}:L{line_no}",
                            target_kind="catch_swallow_hazard",
                            evidences=evidences,
                            location=Location(file_path=m.path, start_line=line_no),
                        ))
        return detections


class MutableStaticFieldRule(BasePatternRule):
    """Detects non-readonly mutable public or internal static fields causing multi-threaded race conditions."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.MUTABLE_STATIC_FIELD

    def detect(self, model: CodeModel) -> list[Detection]:
        detections = []
        # Matches: public static List<T> Field = new(); or public static int Counter;
        mut_static_pattern = re.compile(
            r"^\s*(?:public|internal)\s+static\s+(?!readonly|const)([\w<>,\[\]]+)\s+(\w+)\s*(?:=|;)",
            re.MULTILINE,
        )
        for m in model.all_modules():
            for i, line in enumerate(m.raw_source.splitlines(), 1):
                match = mut_static_pattern.search(line)
                if match and "class " not in line:
                    field_name = match.group(2)
                    evidences = [
                        Evidence(
                            description=f"Mutable static field `{field_name}` introduces cross-thread race condition hazards",
                            weight=0.85,
                            rule_code="HAZARD_MUTABLE_STATIC_FIELD",
                            location=Location(file_path=m.path, start_line=i),
                        )
                    ]
                    detections.append(self._create_detection(
                        target_name=f"{m.namespace}.{m.name}.{field_name}",
                        target_kind="mutable_static_hazard",
                        evidences=evidences,
                        location=Location(file_path=m.path, start_line=i),
                    ))
        return detections
