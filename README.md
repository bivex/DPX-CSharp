<div align="center">

# 🎯 DPX-CSharp

**Multi-Paradigm Hexagonal Architecture & Design Pattern Scanner for C# / .NET**

*Detects 46 architectural patterns, all 23 Gang of Four (GoF) patterns, C# 10–13 idioms, CQRS/MediatR pipelines, Channels concurrency, and async hazards — complete with an interactive IDE Observability HUD.*

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![.NET Support](https://img.shields.io/badge/.NET-6%20%2F%207%20%2F%208%20%2F%209+-512BD4.svg?logo=dotnet&logoColor=white)](https://dotnet.microsoft.com/)
[![C# Version](https://img.shields.io/badge/C%23-10%20--%2013-239120.svg?logo=csharp&logoColor=white)](https://learn.microsoft.com/en-us/dotnet/csharp/)
[![GoF Coverage](https://img.shields.io/badge/GoF%20Patterns-23%2F23%20(100%25)-8A2BE2.svg)](https://en.wikipedia.org/wiki/Design_Patterns)
[![Detection Rules](https://img.shields.io/badge/Rules-46%20Detection%20Rules-00D8FF.svg)](#-catalog-of-46-detection-rules)
[![Architecture](https://img.shields.io/badge/Architecture-Hexagonal%20DDD-9333EA.svg)](https://en.wikipedia.org/wiki/Hexagonal_architecture_(software))
[![Tests](https://img.shields.io/badge/Tests-Passing-35D07F.svg)](#-test-suite)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[**Quick Start**](#-quick-start) •
[**Pattern Catalog**](#-catalog-of-46-detection-rules) •
[**Architecture HUD**](#-architecture-observability-hud) •
[**CLI Reference**](#-cli-commands) •
[**Architecture Design**](#-hexagonal-architecture-design)

</div>

---

## 💡 Overview

**DPX-CSharp** is a deterministic static analysis engine designed specifically for modern C# and .NET codebases (ASP.NET Core, EF Core, Clean Architecture, Microservices, Worker Services).

Unlike standard Roslyn linters, DPX-CSharp analyzes code at the **architectural level**:
- **Zero-Dependency Native Parser:** Parses `.cs` files instantly without invoking `dotnet build` or MSBuild workspace overhead.
- **Complete GoF 23/23 Coverage:** Classifies all classical creational, structural, and behavioral design patterns.
- **Modern C# 10–13 Language Idioms:** Identifies Primary Constructors, `record struct` immutability, Switch Pattern Matching, and Generic Covariance/Contravariance (`out`/`in`).
- **Enterprise & .NET Architecture:** Detects CQRS MediatR Handlers, Repository & Unit of Work, Options Pattern (`IOptions<T>`), and Railway Result / ErrorOr monads.
- **Concurrency & Hazard Guard:** Detects `System.Threading.Channels`, `SemaphoreSlim.WaitAsync()`, `IAsyncEnumerable<T>`, while catching Sync-Over-Async deadlocks (`.Result`), unmanaged `IDisposable` leaks, and blanket `catch (Exception)` swallows.
- **IDE Architecture Observability HUD:** Generates a standalone HTML dashboard with source navigation, metric hotspots, and one-click AI architectural review prompts.

---

## ⚡ Real-World Benchmarks

Tested against real-world .NET and Clean Architecture projects cloned directly from GitHub:

| Repository | Focus Area | Files Scanned | Architectural Findings | Scan Time | Top Architectural Signals |
|---|---|:---:|:---:|:---:|---|
| [**DapperLib/Dapper**](https://github.com/DapperLib/Dapper) | Micro-ORM / High-Perf IL | 51 | 159 | **0.082s** | `async_enumerable_stream`, `expression_tree_linq`, `null_forgiving` (70), `god_class_srp` |
| [**jbogard/MediatR**](https://github.com/jbogard/MediatR) | Mediator Pipeline | 43 | 74 | **0.038s** | `generic_variance_in_out` (13), `mediator_pattern` (8), `primary_constructor` |
| [**ardalis/CleanArchitecture**](https://github.com/ardalis/CleanArchitecture) | Clean Arch Template | 72 | 120 | **0.027s** | `primary_constructor` (18), `railway_result_monad` (14), `mediator_pattern` (5) |
| [**jasontaylordev/CleanArchitecture**](https://github.com/jasontaylordev/CleanArchitecture) | CQRS / EF Core Clean Arch | 76 | 98 | **0.036s** | `mediator_pattern` (12), `command_pattern` (10), `dependency_injection` (6) |
| [**examples/csharp_samples**](./examples/csharp_samples) | GoF 23/23 + Banking + Hazards | 3 | 48 | **0.005s** | All 23 GoF patterns, Channels, Options Pattern, Async Semaphore |
| **TOTAL** | | **245** | **499** | **0.188s** | **~1,300 files/sec throughput** |

---

## 🚀 Quick Start

### 1. Installation

```bash
# Using uv (recommended)
uv pip install -e ".[dev]"

# Or standard pip
pip install -e ".[dev]"
```

### 2. Basic Scan

```bash
# Scan a C# project directory or solution
dpx-cs scan ./src

# Scan and export interactive HTML Architecture HUD report
dpx-cs scan ./src -H reports/architecture_hud.html

# Exclude bin/obj/test folders
dpx-cs scan ./src -e bin -e obj -e tests -H reports/hud.html
```

---

## 🎯 Catalog of 46 Detection Rules

<details open>
<summary><b>1. Type System, Records & Pattern Matching (5 Rules)</b></summary>
<br>

| Rule Identifier | Description | Idiomatic C# Pattern |
|---|---|---|
| `record_struct_immutability` | Value-object immutability with compiler-synthesized equality | `public readonly record struct Money(decimal Amount, string Currency);` |
| `pattern_matching_switch` | Expressive C# 8+ switch expressions with relational patterns | `return shape switch { Circle c => Math.PI * c.R * c.R, _ => 0 };` |
| `primary_constructor` | Primary constructor binding parameters directly to class body | `public class OrderService(IOrderRepo repo, ILogger logger)` |
| `generic_variance_in_out` | Explicit generic covariance (`out T`) & contravariance (`in T`) | `public interface IReadOnlyRepository<out T> { T GetById(Guid id); }` |
| `expression_tree_linq` | `Expression<Func<T, bool>>` expression trees and query mapping | `public IQueryable<T> Filter(Expression<Func<T, bool>> predicate)` |

</details>

<details open>
<summary><b>2. Creational Patterns — Full GoF (5 Rules)</b></summary>
<br>

| Rule Identifier | GoF | Description | Idiomatic C# Pattern |
|---|:---:|---|---|
| `abstract_factory` | ✅ | Product family creation interfaces | `public interface IUIFactory { IButton CreateBtn(); IDialog CreateDlg(); }` |
| `builder_pattern` | ✅ | Fluent chained construction with final `Build()` | `new WebApplicationBuilder().Services.AddSingleton(...).Build();` |
| `factory_method` | ✅ | Static/instance factory encapsulating creation & validation | `public static Result<Email> Create(string raw) => ...` |
| `prototype_clone` | ✅ | Object cloning via `ICloneable` or `with` mutation | `var updated = original with { Status = OrderStatus.Shipped };` |
| `singleton_pattern` | ✅ | Thread-safe single instance with `Lazy<T>` | `private static readonly Lazy<Config> _instance = new(() => new());` |

</details>

<details open>
<summary><b>3. Structural Patterns — Full GoF (7 Rules)</b></summary>
<br>

| Rule Identifier | GoF | Description | Idiomatic C# Pattern |
|---|:---:|---|---|
| `adapter_pattern` | ✅ | Interface wrapper converting incompatible contracts | `public class LegacyPaymentAdapter(LegacyBank bank) : IPaymentGateway` |
| `bridge_pattern` | ✅ | Decouples abstraction from implementation via composition | `public abstract class RemoteControl(IDevice device) { ... }` |
| `composite_pattern` | ✅ | Recursive tree structure treating nodes and leaves uniformly | `public class DirectoryComposite : IFileSystemItem { List<IFileSystemItem> _c; }` |
| `decorator_pattern` | ✅ | Class wrapping same interface adding cross-cutting logic | `public class CachedUserRepo(IUserRepo inner, IMemoryCache cache) : IUserRepo` |
| `facade_pattern` | ✅ | Unified simplified facade over complex subsystems | `public class OrderFacade(IPaymentService pay, IShippingService ship)` |
| `flyweight_pattern` | ✅ | ConcurrentDictionary / ObjectPool sharing instances | `private static readonly ConcurrentDictionary<string, Glyph> _pool;` |
| `proxy_handler` | ✅ | Surrogate class controlling access or lazy loading | `public class SecurityProxy(IResource real, IUserContext ctx) : IResource` |

</details>

<details open>
<summary><b>4. Behavioral Patterns — Full GoF (11 Rules)</b></summary>
<br>

| Rule Identifier | GoF | Description | Idiomatic C# Pattern |
|---|:---:|---|---|
| `chain_of_responsibility` | ✅ | Middleware pipeline request delegation | `public async Task InvokeAsync(HttpContext ctx, RequestDelegate next)` |
| `command_pattern` | ✅ | Encapsulated executable action command objects | `public record CreateOrderCommand(Guid CustId) : IRequest<Result>;` |
| `interpreter_pattern` | ✅ | Expression grammar AST evaluation engine | `public interface IExpression { int Interpret(Context ctx); }` |
| `iterator_yield` | ✅ | Lazy generator state machine using `yield return` | `public static IEnumerable<int> Sequence() { while(true) yield return ++c; }` |
| `mediator_pattern` | ✅ | Central in-process message broker (MediatR) | `public class OrderCtrl(IMediator mediator) { ... mediator.Send(cmd); }` |
| `memento_pattern` | ✅ | State snapshot capture supporting undo/redo | `public class DocumentMemento { public string State { get; init; } }` |
| `observer_event_observable` | ✅ | Pub/Sub notifications via `event EventHandler<T>` | `public event EventHandler<OrderEventArgs>? OrderPlaced;` |
| `state_pattern` | ✅ | State machine altering behavior based on state | `public interface IOrderState { void Process(OrderContext ctx); }` |
| `strategy_pattern` | ✅ | Pluggable interchangeable algorithmic strategies | `public interface IDiscountStrategy { decimal Calculate(decimal total); }` |
| `template_method` | ✅ | Skeleton algorithm deferring steps to abstract hooks | `public abstract class Exporter { public void Run() { Read(); Save(); } }` |
| `visitor_pattern` | ✅ | Double-dispatch separating operations from AST structures | `public interface IASTVisitor { void Visit(BinaryNode n); }` |

</details>

<details open>
<summary><b>5. Enterprise & .NET Architecture (5 Rules)</b></summary>
<br>

| Rule Identifier | Description | Idiomatic C# Pattern |
|---|---|---|
| `cqrs_mediatr_handler` | CQRS request handler separating read/write | `public class CreateOrderHandler : IRequestHandler<CreateOrderCmd, Result>` |
| `repository_unit_of_work` | Domain persistence abstraction decoupling EF Core | `public interface IUnitOfWork { IOrderRepo Orders { get; } Task CommitAsync(); }` |
| `options_pattern_configuration` | Strongly-typed configuration binding | `public class PaymentService(IOptions<StripeOptions> options)` |
| `railway_result_monad` | Total type-safe error handling without exceptions | `public Result<User, Error> Register(Dto dto) => ...` |
| `dependency_injection_service_collection` | IoC container registration extensions | `public static IServiceCollection AddInfra(this IServiceCollection s)` |

</details>

<details open>
<summary><b>6. Concurrency, Channels & TPL (4 Rules)</b></summary>
<br>

| Rule Identifier | Risk | Description | Idiomatic C# Pattern |
|---|:---:|---|---|
| `channel_producer_consumer` | Info | Lock-free high-throughput async queues | `private readonly Channel<Msg> _ch = Channel.CreateBounded<Msg>(1000);` |
| `structured_task_when_all` | Info | Structured parallel task coordination | `await Task.WhenAll(taskA, taskB);` |
| `async_lock_semaphore` | Info | Non-blocking async mutual exclusion | `await _semaphore.WaitAsync(); try { ... } finally { _semaphore.Release(); }` |
| `async_enumerable_stream` | Info | Asynchronous pull-based stream processing | `public async IAsyncEnumerable<Item> StreamAsync([EnumeratorCancellation] ct)` |

</details>

<details open>
<summary><b>7. Resilience & Resource Safety Hazards (5 Rules)</b></summary>
<br>

| Rule Identifier | Severity | Description | Anti-Pattern |
|---|:---:|---|---|
| `sync_over_async_deadlock` | 🔴 High | Thread-pool starvation from sync-over-async blocking | `var data = GetDataAsync().Result;` / `.GetAwaiter().GetResult()` |
| `idisposable_leak_hazard` | 🔴 High | Instantiating unmanaged resource without `using` | `var stream = new MemoryStream();` (Missing `using var`) |
| `null_forgiving_suppression` | ⚠️ Medium | Bypassing nullable reference check with `!` | `string name = customer.Name!;` (NullReferenceException risk) |
| `try_catch_blanket_swallow` | 🔴 High | Silently swallowing exceptions in empty catch | `try { ... } catch (Exception) {}` |
| `mutable_static_field` | ⚠️ Medium | Non-readonly static state causing multi-threaded race conditions | `public static List<Order> ActiveOrders = new();` |

</details>

<details open>
<summary><b>8. Principles & Code Quality (4 Rules)</b></summary>
<br>

| Rule Identifier | Principle | Threshold | Description |
|---|:---:|:---:|---|
| `god_class_srp` | Single Responsibility (SRP) | > 350 LOC | Overly coupled God Class centralizing too many duties |
| `cyclomatic_complexity_kiss` | Keep It Simple (KISS) | > 12 Branches | High nesting and complex branching density |
| `duplicate_code_dry` | Don't Repeat Yourself (DRY) | Repeated blocks | Duplicate implementation logic across independent classes |
| `circular_namespace_dependency` | Clean Dependency Graph | Namespace Cycle | Bidirectional `using` cycles between namespaces |

</details>

---

## 🖥️ Architecture Observability HUD

Run with `-H output.html` to generate an interactive IDE Architecture Dashboard:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│  C#  DPX Architecture HUD   MyDotNetApp   C# / .NET Observability Engine               │
│  📁 120 files  ⏱ 0.14s  🔷 184 findings  🔴 12 action required       [AI Context] [💾]│
├──── ARCHITECTURE HEALTH: ████████████████░░  91% ──────────────────────────────────────┤
├──────────────────┬──────────────────────────────────────────┬──────────────────────────┤
│ ARCHITECTURE NAV │ FINDINGS STREAM           [Density ▾] 🔍 │ INSPECTOR DRAWER         │
│                  │                                          │                          │
│ Views            │ #1  cqrs_mediatr_handler                 │ #1  cqrs_mediatr_handler │
│ 📋 Findings  184 │ Orders.DepositCommandHandler             │ Orders.Commands · Enterp │
│ 🗺️ Hotspots    8 │ 📍 src/Domain/Banking.cs:72:1 • 90% HIGH │                          │
│                  │ ─────────────────────────────────────── │ IMPACT: HIGH             │
│ FILTER           │ #2  sync_over_async_deadlock       🔴    │ CONF:   90% [VERY HIGH]  │
│ ◉ All        184 │ Trading.TradingEngineContext:L42         │                          │
│ 🔴 Action     12 │ 📍 src/Engine/Trading.cs:42:1 • 90% HIGH │ EVIDENCE TRAIL           │
│ 🔷 Type Sys   28 │ ─────────────────────────────────────── │ +90% NET_CQRS_MEDIATR    │
│ 🟢 Creational 24 │ #3  channel_producer_consumer            │ Class implements CQRS    │
│ 🟣 Structural 32 │ Pipeline.TransactionAuditPipeline        │ IRequestHandler contract │
│ 🟠 Behavioral 40 │ 📍 src/Domain/Banking.cs:98:1 • 90% HIGH │ for command execution    │
│ ⚡ Concurr    16 │                                          │                          │
│ 🏛️ Enterprise 32 │                                          │ AI ARCHITECT ACTIONS     │
│                  │                                          │ [💡 Review Architecture] │
│ HOTSPOTS         │                                          │ [🛠️ Refactor Modern C#] │
│ ● Banking.cs  34 │                                          │ [🔍 Explain Finding]     │
│ ● GoF.cs      52 │                                          │                          │
└──────────────────┴──────────────────────────────────────────┴──────────────────────────┘
```

---

## 🛠️ CLI Commands

```bash
# 1. Scan a project directory or solution
dpx-cs scan <path> [OPTIONS]

Options:
  -H, --html <path>     Export interactive HTML Architecture HUD report
  -e, --exclude <dir>   Exclude directory from scan (repeatable)
  -v, --verbose         Output full detection details to console
  --help                Show command help

# 2. View all 46 registered rules with descriptions
dpx-cs rules

# 3. Check CLI version
dpx-cs version
```

---

## 🏛️ Hexagonal Architecture Design

```
src/pattern_detector/
├── domain/                          # Core Domain Logic (Zero external dependencies)
│   ├── value_objects.py             # PatternCategory (8), PatternType (46), Confidence
│   ├── code_model.py                # C# AST models (CSModule, CSClass, CSInterface, CSRecord)
│   ├── detection.py                 # Detection and DetectionReport domain models
│   ├── pattern.py                   # Catalog metadata for all 46 patterns
│   └── rules/                       # 46 decoupled rule evaluators across 8 modules
├── application/                     # Application Use Cases
│   └── detection_service.py         # DetectionService orchestrator
├── ports/                           # Input and Output boundary interfaces
│   ├── inbound.py                   # ScanProjectUseCase protocol
│   └── outbound.py                  # ReportFormatterPort, ResultRepositoryPort
└── adapters/                        # Infrastructure Adapters
    ├── inbound/cli/main.py          # Typer & Rich CLI
    └── outbound/
        ├── parsers/
        │   └── native_cs_parser_adapter.py   # High-speed native C# parser
        └── persistence/
            └── html_report_formatter.py      # Architecture Observability HUD generator
```

---

## 🧪 Test Suite

```bash
uv run pytest tests/ -v
```

---

---

## 🌐 The DPX Multi-Language Static Analysis Family (33 Languages)

| # | Language | Repository | Ecosystem & Focus |
|:---:|---|---|---|
| 1 | **Ada** | [`bivex/DPX-Ada`](https://github.com/bivex/DPX-Ada) | Ada 2012/2022, SPARK Contracts, Ravenscar Tasking, DO-178C Safety |
| 2 | **Clojure** | [`bivex/DPX`](https://github.com/bivex/DPX) | Lisp S-Expressions, Protocols, Multimethods |
| 3 | **C** | [`bivex/DPX-C`](https://github.com/bivex/DPX-C) | Memory Safety, Struct VTables, Idiomatic C11/C23 |
| 4 | **Cairo** | [`bivex/DPX-Cairo`](https://github.com/bivex/DPX-Cairo) | Starknet Smart Contracts, ZK-Rollup Invariants |
| 5 | **C++** | [`bivex/DPX-Cpp`](https://github.com/bivex/DPX-Cpp) | RAII, CRTP, Concepts, Modern C++20/23 |
| 6 | **C#** | [`bivex/DPX-CSharp`](https://github.com/bivex/DPX-CSharp) | .NET 9, Roslyn AST, Linq, Records |
| 7 | **Dart** | [`bivex/DPX-Dart`](https://github.com/bivex/DPX-Dart) | Dart 3.x, Flutter, BLoC, Riverpod, Isolates |
| 8 | **Elixir** | [`bivex/DPX-Elixir`](https://github.com/bivex/DPX-Elixir) | BEAM OTP, GenServer, Supervisors |
| 9 | **Erlang** | [`bivex/DPX-Erlang`](https://github.com/bivex/DPX-Erlang) | Fault Tolerance, Actor Model, OTP Behaviors |
| 10 | **Gleam** | [`bivex/DPX-Gleam`](https://github.com/bivex/DPX-Gleam) | Type-Safe BEAM, Actor Concurrency |
| 11 | **Go** | [`bivex/DPX-Go`](https://github.com/bivex/DPX-Go) | Goroutines, Channels, Composition, Interfaces |
| 12 | **Haskell** | [`bivex/DPX-Haskell`](https://github.com/bivex/DPX-Haskell) | Pure Functional, Monads, Typeclasses, Arrows |
| 13 | **Huff** | [`bivex/DPX-Huff`](https://github.com/bivex/DPX-Huff) | Low-Level EVM Bytecode & Opcodes |
| 14 | **Idris 2** | [`bivex/DPX-Idris2`](https://github.com/bivex/DPX-Idris2) | Dependent Types, QTT Linear Protocols, Totality, Proofs |
| 15 | **Java** | [`bivex/DPX-Java`](https://github.com/bivex/DPX-Java) | Spring Boot, Enterprise Java, JVM Invariants |
| 16 | **Julia** | [`bivex/DPX-Julia`](https://github.com/bivex/DPX-Julia) | Multiple Dispatch, Scientific Computing |
| 17 | **Kotlin** | [`bivex/DPX-Kotlin`](https://github.com/bivex/DPX-Kotlin) | Coroutines, Multiplatform, Functional DSLs |
| 18 | **Lua** | [`bivex/DPX-Lua`](https://github.com/bivex/DPX-Lua) | Metatables, Coroutines, LuaJIT, Neovim |
| 19 | **Mojo** | [`bivex/DPX-Mojo`](https://github.com/bivex/DPX-Mojo) | SIMD Hardware, Memory Lifetimes, AI Systems |
| 20 | **Move** | [`bivex/DPX-Move`](https://github.com/bivex/DPX-Move) | Aptos & Sui Resource Safety, Linear Types |
| 21 | **OCaml** | [`bivex/DPX-OCaml`](https://github.com/bivex/DPX-OCaml) | Algebraic Data Types, Functors, Polymorphism |
| 22 | **PHP** | [`bivex/DPX-Php`](https://github.com/bivex/DPX-Php) | Modern PHP 8.4, Attributes, Traits, Laravel |
| 23 | **Prolog** | [`bivex/DPX-Prolog`](https://github.com/bivex/DPX-Prolog) | ISO Prolog, SWI-Prolog, DCG, CLP(FD/R/Q), CHR, Meta-Interpreters |
| 24 | **Puppet** | [`bivex/DPX-Puppet`](https://github.com/bivex/DPX-Puppet) | Puppet DSL, Roles/Profiles, IaC Security, Hiera |
| 25 | **Python** | [`bivex/DPX-Py`](https://github.com/bivex/DPX-Py) | Metaprogramming, Protocols, Hexagonal DDD |
| 26 | **Ruby** | [`bivex/DPX-Ruby`](https://github.com/bivex/DPX-Ruby) | Ruby 3.x, Rails, Metaprogramming, Dry-RB, Security |
| 27 | **Rust** | [`bivex/DPX-Rust`](https://github.com/bivex/DPX-Rust) | Zero-Cost Abstractions, Borrow Checker, Traits |
| 28 | **Solidity** | [`bivex/DPX-Solidity`](https://github.com/bivex/DPX-Solidity) | DeFi Security, Reentrancy, EVM Yul/Assembly |
| 29 | **SQL** | [`bivex/DPX-SQL`](https://github.com/bivex/DPX-SQL) | PostgreSQL, MySQL, SQLite, T-SQL, PL/SQL |
| 30 | **Swift** | [`bivex/DPX-Swift`](https://github.com/bivex/DPX-Swift) | Protocol-Oriented Programming, Actors |
| 31 | **TypeScript** | [`bivex/DPX-TypeScript`](https://github.com/bivex/DPX-TypeScript) | Generics, Conditional Types, Clean Architecture |
| 32 | **Yul** | [`bivex/DPX-Yul`](https://github.com/bivex/DPX-Yul) | EVM Intermediate Representation Optimization |
| 33 | **Zig** | [`bivex/DPX-Zig`](https://github.com/bivex/DPX-Zig) | Comptime, Manual Memory Allocators, C ABI |

---

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
