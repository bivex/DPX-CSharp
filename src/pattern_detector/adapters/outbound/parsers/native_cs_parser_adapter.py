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
    """Zero-dependency high-speed parser for C# (.cs) source files."""

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
        m = re.search(r"^\s*namespace\s+([\w\.]+)\s*[;\{]", content, re.MULTILINE)
        if m:
            return m.group(1)
        return "Global"

    def _parse_usings(self, content: str) -> list[str]:
        usings = []
        for line in content.splitlines():
            line_s = line.strip()
            if line_s.startswith("using ") and line_s.endswith(";"):
                m = re.match(r"^using\s+(?:static\s+)?([\w\.]+)\s*;", line_s)
                if m:
                    usings.append(m.group(1))
        return usings

    def _parse_records(self, content: str, file_path: str) -> dict[str, CSRecord]:
        records: dict[str, CSRecord] = {}
        for i, line in enumerate(content.splitlines(), 1):
            line_s = line.strip()
            if not line_s or line_s.startswith("//") or line_s.startswith("/*") or line_s.startswith("*"):
                continue
            if " record " in line_s or line_s.startswith("record "):
                m = re.search(r"\brecord\s+(struct|class)?\s*([A-Za-z0-9_]+)(?:<[^>]+>)?(?:\((.*?)\))?(?:\s*:\s*([^{;]+))?", line_s)
                if m:
                    kind = m.group(1) or "class"
                    name = m.group(2)
                    params_raw = m.group(3) or ""
                    bases_raw = m.group(4) or ""

                    params = [p.strip() for p in params_raw.split(",") if p.strip()]
                    bases = [b.split("where")[0].split("{")[0].strip() for b in bases_raw.split(",") if b.strip()]
                    clean_bases = [b for b in bases if b]

                    is_ro = "readonly " in line_s
                    records[name] = CSRecord(
                        name=name,
                        is_struct=(kind == "struct"),
                        is_readonly=is_ro,
                        parameters=params,
                        implements_list=clean_bases,
                        location=Location(file_path=file_path, start_line=i),
                    )
        return records

    def _parse_interfaces(self, content: str, file_path: str) -> dict[str, CSInterface]:
        interfaces: dict[str, CSInterface] = {}
        for i, line in enumerate(content.splitlines(), 1):
            line_s = line.strip()
            if not line_s or line_s.startswith("//") or line_s.startswith("/*") or line_s.startswith("*"):
                continue
            if " interface " in line_s or line_s.startswith("interface "):
                m = re.search(r"\binterface\s+([A-Za-z0-9_]+)(?:<([^>]+)>)?(?:\s*:\s*([^{]+))?", line_s)
                if m:
                    name = m.group(1)
                    generics = m.group(2) or ""
                    bases_raw = m.group(3) or ""
                    bases = [b.split("where")[0].split("{")[0].strip() for b in bases_raw.split(",") if b.strip()]
                    clean_bases = [b for b in bases if b]

                    has_in_out = "out " in generics or "in " in generics

                    methods = []
                    lines_to_scan = content.splitlines()[i - 1 : min(len(content.splitlines()), i + 40)]
                    for idx, l in enumerate(lines_to_scan):
                        if idx > 0 and "}" in l and "{" not in l:
                            break
                        chunk = l[l.find("{"):] if "{" in l else l
                        for mm in re.finditer(r"([A-Za-z0-9_\.<>\[\]\?]+)\s+([A-Za-z0-9_]+)\s*\(", chunk):
                            mth_name = mm.group(2)
                            if mth_name not in ("get", "set", "interface", "where", "if", "for", "while"):
                                methods.append(mth_name)

                    interfaces[name] = CSInterface(
                        name=name,
                        extends_list=clean_bases,
                        methods=methods,
                        is_generic=bool(generics),
                        has_in_out_variance=has_in_out,
                        location=Location(file_path=file_path, start_line=i),
                    )
        return interfaces

    def _parse_classes(self, content: str, file_path: str) -> dict[str, CSClass]:
        classes: dict[str, CSClass] = {}
        for i, line in enumerate(content.splitlines(), 1):
            line_s = line.strip()
            if not line_s or line_s.startswith("//") or line_s.startswith("/*") or line_s.startswith("*"):
                continue
            if " class " in line_s or line_s.startswith("class "):
                if "record " in line_s:
                    continue
                m = re.search(r"\bclass\s+([A-Za-z0-9_]+)(?:<[^>]+>)?(?:\((.*?)\))?(?:\s*:\s*([^{]+))?", line_s)
                if m:
                    name = m.group(1)
                    primary_ctor = m.group(2)
                    bases_raw = m.group(3) or ""
                    bases = [b.split("where")[0].split("{")[0].strip() for b in bases_raw.split(",") if b.strip()]
                    clean_bases = [b for b in bases if b]

                    extends_name = clean_bases[0] if clean_bases and not clean_bases[0].startswith("I") else None
                    implements_list = [b for b in clean_bases if b != extends_name]

                    constructor_params = [p.strip() for p in primary_ctor.split(",") if p.strip()] if primary_ctor else []
                    is_abstract = "abstract " in line_s
                    is_sealed = "sealed " in line_s
                    is_static = "static " in line_s

                    classes[name] = CSClass(
                        name=name,
                        extends_name=extends_name,
                        implements_list=implements_list,
                        modifiers=["public" if "public " in line_s else "internal"],
                        constructor_params=constructor_params,
                        is_abstract=is_abstract,
                        is_sealed=is_sealed,
                        is_static=is_static,
                        has_primary_constructor=bool(primary_ctor is not None),
                        location=Location(file_path=file_path, start_line=i),
                    )
        return classes

    def _parse_structs(self, content: str, file_path: str) -> dict[str, CSStruct]:
        structs: dict[str, CSStruct] = {}
        for i, line in enumerate(content.splitlines(), 1):
            line_s = line.strip()
            if not line_s or line_s.startswith("//") or line_s.startswith("/*") or line_s.startswith("*"):
                continue
            if " struct " in line_s or line_s.startswith("struct "):
                if "record " in line_s:
                    continue
                m = re.search(r"\bstruct\s+([A-Za-z0-9_]+)(?:<[^>]+>)?(?:\s*:\s*([^{]+))?", line_s)
                if m:
                    name = m.group(1)
                    bases_raw = m.group(2) or ""
                    bases = [b.split("where")[0].split("{")[0].strip() for b in bases_raw.split(",") if b.strip()]
                    clean_bases = [b for b in bases if b]

                    is_ro = "readonly " in line_s
                    is_ref = "ref " in line_s

                    structs[name] = CSStruct(
                        name=name,
                        is_readonly=is_ro,
                        is_ref=is_ref,
                        implements_list=clean_bases,
                        location=Location(file_path=file_path, start_line=i),
                    )
        return structs

    def _parse_enums(self, content: str, file_path: str) -> dict[str, CSEnum]:
        enums: dict[str, CSEnum] = {}
        for i, line in enumerate(content.splitlines(), 1):
            line_s = line.strip()
            if not line_s or line_s.startswith("//") or line_s.startswith("/*") or line_s.startswith("*"):
                continue
            if " enum " in line_s or line_s.startswith("enum "):
                m = re.search(r"\benum\s+([A-Za-z0-9_]+)", line_s)
                if m:
                    name = m.group(1)
                    is_flags = "[Flags]" in content[:content.find(line) + len(line)]
                    enums[name] = CSEnum(
                        name=name,
                        is_flags=is_flags,
                        location=Location(file_path=file_path, start_line=i),
                    )
        return enums
