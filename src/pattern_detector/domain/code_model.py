"""AST & Semantic Code Model abstractions for C# source files."""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field
from pattern_detector.domain.value_objects import Location


class CSMethod(BaseModel):
    """C# Method declaration."""

    name: str
    return_type: str = "void"
    parameters: list[str] = Field(default_factory=list)
    modifiers: list[str] = Field(default_factory=list)
    attributes: list[str] = Field(default_factory=list)
    is_async: bool = False
    is_static: bool = False
    is_abstract: bool = False
    is_override: bool = False
    is_virtual: bool = False
    is_generic: bool = False
    location: Location | None = None


class CSProperty(BaseModel):
    """C# Property declaration."""

    name: str
    property_type: str = "object"
    modifiers: list[str] = Field(default_factory=list)
    has_getter: bool = True
    has_setter: bool = True
    is_init_only: bool = False
    is_static: bool = False
    location: Location | None = None


class CSField(BaseModel):
    """C# Field declaration."""

    name: str
    field_type: str = "object"
    modifiers: list[str] = Field(default_factory=list)
    is_readonly: bool = False
    is_static: bool = False
    is_const: bool = False
    location: Location | None = None


class CSInterface(BaseModel):
    """C# Interface declaration."""

    name: str
    extends_list: list[str] = Field(default_factory=list)
    methods: list[str] = Field(default_factory=list)
    properties: list[str] = Field(default_factory=list)
    is_generic: bool = False
    has_in_out_variance: bool = False
    location: Location | None = None


class CSRecord(BaseModel):
    """C# Record or Record Struct declaration."""

    name: str
    is_struct: bool = False
    is_readonly: bool = False
    implements_list: list[str] = Field(default_factory=list)
    parameters: list[str] = Field(default_factory=list)
    location: Location | None = None


class CSClass(BaseModel):
    """C# Class declaration."""

    name: str
    extends_name: str | None = None
    implements_list: list[str] = Field(default_factory=list)
    modifiers: list[str] = Field(default_factory=list)
    attributes: list[str] = Field(default_factory=list)
    constructor_params: list[str] = Field(default_factory=list)
    methods: dict[str, CSMethod] = Field(default_factory=dict)
    properties: dict[str, CSProperty] = Field(default_factory=dict)
    fields: dict[str, CSField] = Field(default_factory=dict)
    is_abstract: bool = False
    is_sealed: bool = False
    is_static: bool = False
    is_generic: bool = False
    has_primary_constructor: bool = False
    location: Location | None = None


class CSStruct(BaseModel):
    """C# Struct declaration."""

    name: str
    is_readonly: bool = False
    is_ref: bool = False
    implements_list: list[str] = Field(default_factory=list)
    location: Location | None = None


class CSEnum(BaseModel):
    """C# Enum declaration."""

    name: str
    members: list[str] = Field(default_factory=list)
    is_flags: bool = False
    location: Location | None = None


class CSModule(BaseModel):
    """Represents a single parsed C# source file (.cs)."""

    path: str
    namespace: str = ""
    usings: list[str] = Field(default_factory=list)
    classes: dict[str, CSClass] = Field(default_factory=dict)
    interfaces: dict[str, CSInterface] = Field(default_factory=dict)
    records: dict[str, CSRecord] = Field(default_factory=dict)
    structs: dict[str, CSStruct] = Field(default_factory=dict)
    enums: dict[str, CSEnum] = Field(default_factory=dict)
    raw_source: str = ""
    line_count: int = 0
    location: Location | None = None

    @property
    def name(self) -> str:
        """Module file stem name."""
        import os
        return os.path.splitext(os.path.basename(self.path))[0]


class CodeModel(BaseModel):
    """Aggregated AST and semantic index for a whole C# codebase."""

    modules: dict[str, CSModule] = Field(default_factory=dict)

    def add_module(self, module: CSModule) -> None:
        self.modules[module.path] = module

    def get_module(self, path: str) -> CSModule | None:
        return self.modules.get(path)

    def all_modules(self) -> list[CSModule]:
        return list(self.modules.values())

    @property
    def total_modules(self) -> int:
        return len(self.modules)
