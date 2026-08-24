"""Native layout and regex-based C# parser adapter (.NET 6-9+, C# 10-13)."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Sequence

from pattern_detector.domain.code_model import (
    CSClass,
    CSEnum,
    CSField,
    CSInterface,
    CSMethod,
    CSModule,
    CSProperty,
    CSRecord,
    CSStruct,
    CodeModel,
)
from pattern_detector.domain.value_objects import Location

CS_EXTENSIONS = {".cs"}
EXCLUDE_DIRS = {
    "bin", "obj", ".vs", ".git", ".idea", ".vscode", "TestResults",
    "node_modules", "dist", "packages",
}


class NativeCSharpParserAdapter:
    """Zero-dependency parser for C# (.cs) source files."""

    def parse_project(self, project_path: str, excludes: Sequence[str] | None = None) -> CodeModel:
        """Parse all C# files in the directory into a CodeModel."""
        model = CodeModel()
        proj_p = Path(project_path)
        all_excludes = set(EXCLUDE_DIRS)
        if excludes:
            all_excludes.update(excludes)

        if proj_p.is_file() and proj_p.suffix in CS_EXTENSIONS:
            mod = self.parse_file(str(proj_p))
            if mod:
                model.add_module(mod)
            return model

        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in all_excludes and not d.startswith(".")]
            for file in files:
                if any(file.endswith(ext) for ext in CS_EXTENSIONS) and not file.endswith(".Designer.cs") and not file.endswith(".g.cs"):
                    fpath = os.path.join(root, file)
                    mod = self.parse_file(fpath)
                    if mod:
                        model.add_module(mod)

        return model

    def parse_file(self, file_path: str) -> CSModule | None:
        """Parse a single C# source file."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception:
            return None

        lines = content.splitlines()
        mod = CSModule(
            path=file_path,
            raw_source=content,
            line_count=len(lines),
            location=Location(file_path=file_path, start_line=1),
        )

        mod.namespace = self._parse_namespace(content)
        mod.usings = self._parse_usings(content)
        mod.records = self._parse_records(content, file_path)
        mod.interfaces = self._parse_interfaces(content, file_path)
        mod.classes = self._parse_classes(content, file_path)
        mod.structs = self._parse_structs(content, file_path)
        mod.enums = self._parse_enums(content, file_path)

        return mod

    def _parse_namespace(self, content: str) -> str:
        # File-scoped: namespace Foo.Bar;
        m = re.search(r"^\s*namespace\s+([\w\.]+)\s*;", content, re.MULTILINE)
        if m:
            return m.group(1)
        # Block-scoped: namespace Foo.Bar {
        m = re.search(r"^\s*namespace\s+([\w\.]+)\s*\{", content, re.MULTILINE)
        if m:
            return m.group(1)
        return "Global"

    def _parse_usings(self, content: str) -> list[str]:
        usings = []
        for line in content.splitlines():
            m = re.match(r"^\s*using\s+(?:static\s+)?([\w\.]+)\s*;", line)
            if m:
                usings.append(m.group(1))
        return usings

    def _parse_records(self, content: str, file_path: str) -> dict[str, CSRecord]:
        records: dict[str, CSRecord] = {}
        # Matches: public readonly record struct Money(...) : IFoo
        # or: public record User(string Name, int Age);
        pattern = re.compile(
            r"^\s*(?:\[[^\]]+\]\s*)*(?:public|internal|private|protected)?\s*(?:(readonly)\s+)?record\s+(struct|class)?\s*(\w+)(?:<[^>]+>)?\s*(?:\((.*?)\))?(?:\s*:\s*([\w\s,<>]+))?",
            re.MULTILINE,
        )
        for i, line in enumerate(content.splitlines(), 1):
            for match in pattern.finditer(line):
                is_ro = bool(match.group(1))
                kind = match.group(2) or "class"
                name = match.group(3)
                params_raw = match.group(4) or ""
                bases_raw = match.group(5) or ""

                params = [p.strip() for p in params_raw.split(",") if p.strip()]
                bases = [b.strip() for b in bases_raw.split(",") if b.strip()]

                records[name] = CSRecord(
                    name=name,
                    is_struct=(kind == "struct"),
                    is_readonly=is_ro,
                    parameters=params,
                    implements_list=bases,
                    location=Location(file_path=file_path, start_line=i),
                )
        return records

    def _parse_interfaces(self, content: str, file_path: str) -> dict[str, CSInterface]:
        interfaces: dict[str, CSInterface] = {}
        pattern = re.compile(
            r"^\s*(?:\[[^\]]+\]\s*)*(?:public|internal|private|protected)?\s*interface\s+(\w+)(?:<([^>]+)>)?(?:\s*:\s*([\w\s,<>]+))?",
            re.MULTILINE,
        )
        for i, line in enumerate(content.splitlines(), 1):
            m = pattern.search(line)
            if m:
                name = m.group(1)
                generics = m.group(2) or ""
                bases_raw = m.group(3) or ""
                bases = [b.strip() for b in bases_raw.split(",") if b.strip()]

                has_in_out = "out " in generics or "in " in generics

                # Scan methods inside interface (including single-line interfaces)
                methods = []
                method_pat = re.compile(r"([\w\.<>\[\]\?]+)\s+(\w+)\s*\(", re.MULTILINE)
                lines_to_scan = content.splitlines()[i - 1 : min(len(content.splitlines()), i + 40)]
                for idx, l in enumerate(lines_to_scan):
                    if idx > 0 and "}" in l and "{" not in l:
                        break
                    # If this is the interface declaration line, search after the '{'
                    chunk = l[l.find("{"):] if "{" in l else l
                    for mm in method_pat.finditer(chunk):
                        if mm.group(2) not in ("get", "set", "interface"):
                            methods.append(mm.group(2))

                interfaces[name] = CSInterface(
                    name=name,
                    extends_list=bases,
                    methods=methods,
                    is_generic=bool(generics),
                    has_in_out_variance=has_in_out,
                    location=Location(file_path=file_path, start_line=i),
                )
        return interfaces

    def _parse_classes(self, content: str, file_path: str) -> dict[str, CSClass]:
        classes: dict[str, CSClass] = {}
        # Regex for class: [Attr] public abstract class Foo<T>(IBar bar) : BaseClass, IFoo
        pattern = re.compile(
            r"^\s*(?:\[([^\]]+)\]\s*)*(?:(public|internal|private|protected)\s+)?(?:(abstract|sealed|static|partial)\s+)?class\s+(\w+)(?:<[^>]+>)?(?:\((.*?)\))?(?:\s*:\s*([\w\s,<>]+))?",
            re.MULTILINE,
        )
        lines = content.splitlines()
        for i, line in enumerate(lines, 1):
            m = pattern.search(line)
            if m and "record " not in line:
                attr_raw = m.group(1) or ""
                visibility = m.group(2) or "internal"
                modifier = m.group(3) or ""
                name = m.group(4)
                primary_ctor = m.group(5)
                bases_raw = m.group(6) or ""

                bases = [b.strip() for b in bases_raw.split(",") if b.strip()]
                extends_name = bases[0] if bases and not bases[0].startswith("I") else None
                implements_list = [b for b in bases if b != extends_name]

                constructor_params = []
                if primary_ctor:
                    constructor_params = [p.strip() for p in primary_ctor.split(",") if p.strip()]

                attrs = [a.strip() for a in attr_raw.split(",") if a.strip()]

                classes[name] = CSClass(
                    name=name,
                    extends_name=extends_name,
                    implements_list=implements_list,
                    modifiers=[visibility] + ([modifier] if modifier else []),
                    attributes=attrs,
                    constructor_params=constructor_params,
                    is_abstract=(modifier == "abstract"),
                    is_sealed=(modifier == "sealed"),
                    is_static=(modifier == "static"),
                    has_primary_constructor=bool(primary_ctor is not None),
                    location=Location(file_path=file_path, start_line=i),
                )
        return classes

    def _parse_structs(self, content: str, file_path: str) -> dict[str, CSStruct]:
        structs: dict[str, CSStruct] = {}
        pattern = re.compile(
            r"^\s*(?:(readonly|ref)\s+)?struct\s+(\w+)(?:\s*:\s*([\w\s,<>]+))?",
            re.MULTILINE,
        )
        for i, line in enumerate(content.splitlines(), 1):
            if "record " in line:
                continue
            m = pattern.search(line)
            if m:
                mod = m.group(1) or ""
                name = m.group(2)
                bases_raw = m.group(3) or ""
                bases = [b.strip() for b in bases_raw.split(",") if b.strip()]

                structs[name] = CSStruct(
                    name=name,
                    is_readonly=(mod == "readonly"),
                    is_ref=(mod == "ref"),
                    implements_list=bases,
                    location=Location(file_path=file_path, start_line=i),
                )
        return structs

    def _parse_enums(self, content: str, file_path: str) -> dict[str, CSEnum]:
        enums: dict[str, CSEnum] = {}
        pattern = re.compile(r"^\s*(?:\[Flags\]\s*)?(?:public|internal)?\s*enum\s+(\w+)", re.MULTILINE)
        for i, line in enumerate(content.splitlines(), 1):
            m = pattern.search(line)
            if m:
                name = m.group(1)
                is_flags = "[Flags]" in content[:content.find(line) + len(line)]
                enums[name] = CSEnum(
                    name=name,
                    is_flags=is_flags,
                    location=Location(file_path=file_path, start_line=i),
                )
        return enums
