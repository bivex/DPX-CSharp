"""Pattern metadata catalog and descriptions for C# / .NET."""

from __future__ import annotations

from pydantic import BaseModel
from pattern_detector.domain.value_objects import PatternCategory, PatternType


class PatternCatalogEntry(BaseModel):
    """Metadata description of a C# pattern rule."""

    pattern_type: PatternType
    category: PatternCategory
    name: str
    description: str
    idiomatic_example: str


PATTERN_CATALOG: dict[PatternType, PatternCatalogEntry] = {
    # ── 1. Type System, Records & Pattern Matching ────────────────────────────
    PatternType.RECORD_STRUCT_IMMUTABILITY: PatternCatalogEntry(
        pattern_type=PatternType.RECORD_STRUCT_IMMUTABILITY,
        category=PatternCategory.TYPE_SYSTEM,
        name="Record / Readonly Struct Immutability",
        description="Immutable value semantics using C# `record`, `readonly record struct`, or positional records (`with { ... }`).",
        idiomatic_example="public readonly record struct Money(decimal Amount, string Currency);",
    ),
    PatternType.PATTERN_MATCHING_SWITCH: PatternCatalogEntry(
        pattern_type=PatternType.PATTERN_MATCHING_SWITCH,
        category=PatternCategory.TYPE_SYSTEM,
        name="Pattern Matching & Switch Expressions",
        description="Type-safe expressive pattern matching using C# 8+ switch expressions with relational, property, and positional patterns.",
        idiomatic_example="return shape switch { Circle c => Math.PI * c.Radius * c.Radius, Rect r => r.W * r.H, _ => 0 };",
    ),
    PatternType.PRIMARY_CONSTRUCTOR: PatternCatalogEntry(
        pattern_type=PatternType.PRIMARY_CONSTRUCTOR,
        category=PatternCategory.TYPE_SYSTEM,
        name="Primary Constructor",
        description="Concise dependency and property binding directly on class or record header declarations (C# 12+).",
        idiomatic_example="public class OrderService(IOrderRepository repo, ILogger<OrderService> logger) { ... }",
    ),
    PatternType.GENERIC_VARIANCE_IN_OUT: PatternCatalogEntry(
        pattern_type=PatternType.GENERIC_VARIANCE_IN_OUT,
        category=PatternCategory.TYPE_SYSTEM,
        name="Generic Covariance & Contravariance",
        description="Explicit type-safe interface and delegate variance via `out T` (covariance) and `in T` (contravariance) modifiers.",
        idiomatic_example="public interface IReadOnlyRepository<out T> { T GetById(int id); }",
    ),
    PatternType.EXPRESSION_TREE_LINQ: PatternCatalogEntry(
        pattern_type=PatternType.EXPRESSION_TREE_LINQ,
        category=PatternCategory.TYPE_SYSTEM,
        name="Expression Trees & LINQ Query Syntax",
        description="Metaprogramming and query translation using `Expression<Func<T, bool>>` for EF Core or custom AST evaluation.",
        idiomatic_example="public IQueryable<T> Filter(Expression<Func<T, bool>> predicate) => _dbSet.Where(predicate);",
    ),

    # ── 2. Creational Patterns — Full GoF ──────────────────────────────────────
    PatternType.ABSTRACT_FACTORY: PatternCatalogEntry(
        pattern_type=PatternType.ABSTRACT_FACTORY,
        category=PatternCategory.CREATIONAL,
        name="Abstract Factory",
        description="Interface declaring factory methods for creating families of related objects without specifying concrete classes.",
        idiomatic_example="public interface IUIFactory { IButton CreateButton(); IDialog CreateDialog(); }",
    ),
    PatternType.BUILDER_PATTERN: PatternCatalogEntry(
        pattern_type=PatternType.BUILDER_PATTERN,
        category=PatternCategory.CREATIONAL,
        name="Builder Pattern",
        description="Fluent step-by-step object construction separating representation from the construction algorithm.",
        idiomatic_example="var app = WebApplication.CreateBuilder(args).Build();",
    ),
    PatternType.FACTORY_METHOD: PatternCatalogEntry(
        pattern_type=PatternType.FACTORY_METHOD,
        category=PatternCategory.CREATIONAL,
        name="Factory Method",
        description="Static or instance factory method encapsulating object creation logic and domain invariant validation.",
        idiomatic_example="public static Result<Email> Create(string raw) => raw.Contains('@') ? Result.Ok(new Email(raw)) : Result.Fail('Invalid');",
    ),
    PatternType.PROTOTYPE_CLONE: PatternCatalogEntry(
        pattern_type=PatternType.PROTOTYPE_CLONE,
        category=PatternCategory.CREATIONAL,
        name="Prototype / Clone Pattern",
        description="Cloning objects via `ICloneable`, memberwise clone, or record `with` non-destructive mutation.",
        idiomatic_example="var updated = original with { Status = OrderStatus.Shipped };",
    ),
    PatternType.SINGLETON_PATTERN: PatternCatalogEntry(
        pattern_type=PatternType.SINGLETON_PATTERN,
        category=PatternCategory.CREATIONAL,
        name="Singleton Pattern",
        description="Thread-safe single instance initialization via `Lazy<T>`, private constructor, or DI singleton lifetime.",
        idiomatic_example="private static readonly Lazy<Singleton> _instance = new(() => new Singleton()); public static Singleton Instance => _instance.Value;",
    ),

    # ── 3. Structural Patterns — Full GoF ──────────────────────────────────────
    PatternType.ADAPTER_PATTERN: PatternCatalogEntry(
        pattern_type=PatternType.ADAPTER_PATTERN,
        category=PatternCategory.STRUCTURAL,
        name="Adapter Pattern",
        description="Converting the interface of a class into another interface expected by clients.",
        idiomatic_example="public class LegacyPaymentAdapter(LegacyBankService bank) : IPaymentGateway { ... }",
    ),
    PatternType.BRIDGE_PATTERN: PatternCatalogEntry(
        pattern_type=PatternType.BRIDGE_PATTERN,
        category=PatternCategory.STRUCTURAL,
        name="Bridge Pattern",
        description="Decoupling an abstraction from its implementation so that both can vary independently via composition.",
        idiomatic_example="public abstract class RemoteControl(IDevice device) { public void Toggle() => device.Enable(); }",
    ),
    PatternType.COMPOSITE_PATTERN: PatternCatalogEntry(
        pattern_type=PatternType.COMPOSITE_PATTERN,
        category=PatternCategory.STRUCTURAL,
        name="Composite / Tree Hierarchy",
        description="Composing objects into tree structures to represent part-whole hierarchies uniformly (`IComponent`, `Composite.Children`).",
        idiomatic_example="public class MenuItemComposite : IMenuComponent { private List<IMenuComponent> _children; }",
    ),
    PatternType.DECORATOR_PATTERN: PatternCatalogEntry(
        pattern_type=PatternType.DECORATOR_PATTERN,
        category=PatternCategory.STRUCTURAL,
        name="Decorator / Aspect Pattern",
        description="Dynamically wrapping an interface implementation to add behavior (caching, logging, resilience).",
        idiomatic_example="public class CachedUserRepository(IUserRepository inner, IMemoryCache cache) : IUserRepository { ... }",
    ),
    PatternType.FACADE_PATTERN: PatternCatalogEntry(
        pattern_type=PatternType.FACADE_PATTERN,
        category=PatternCategory.STRUCTURAL,
        name="Facade Pattern",
        description="Providing a unified, simplified interface to a complex subsystem or set of external service clients.",
        idiomatic_example="public class OrderProcessingFacade(IInventoryService inv, IPaymentService pay, IShippingService ship) { ... }",
    ),
    PatternType.FLYWEIGHT_PATTERN: PatternCatalogEntry(
        pattern_type=PatternType.FLYWEIGHT_PATTERN,
        category=PatternCategory.STRUCTURAL,
        name="Flyweight / Object Pool",
        description="Sharing fine-grained immutable instances using `ConcurrentDictionary` or `ArrayPool<T>`/`ObjectPool<T>`.",
        idiomatic_example="private static readonly ConcurrentDictionary<string, Glyph> _pool = new();",
    ),
    PatternType.PROXY_HANDLER: PatternCatalogEntry(
        pattern_type=PatternType.PROXY_HANDLER,
        category=PatternCategory.STRUCTURAL,
        name="Proxy Pattern",
        description="Providing a surrogate or placeholder to control access, perform lazy loading, or intercept invocations.",
        idiomatic_example="public class SecurityProxy(IRealSubject real, IUserContext user) : IRealSubject { ... }",
    ),

    # ── 4. Behavioral Patterns — Full GoF ──────────────────────────────────────
    PatternType.CHAIN_OF_RESPONSIBILITY: PatternCatalogEntry(
        pattern_type=PatternType.CHAIN_OF_RESPONSIBILITY,
        category=PatternCategory.BEHAVIORAL,
        name="Chain of Responsibility / Middleware Pipeline",
        description="Passing requests along a dynamic handler chain (ASP.NET Core Middleware `RequestDelegate`, pipeline behaviors).",
        idiomatic_example="public async Task InvokeAsync(HttpContext ctx, RequestDelegate next) { await next(ctx); }",
    ),
    PatternType.COMMAND_PATTERN: PatternCatalogEntry(
        pattern_type=PatternType.COMMAND_PATTERN,
        category=PatternCategory.BEHAVIORAL,
        name="Command Pattern",
        description="Encapsulating a request as an object, allowing parameterization and undoable transaction execution.",
        idiomatic_example="public record CreateOrderCommand(int CustomerId, decimal Total) : IRequest<Result<OrderDto>>;",
    ),
    PatternType.INTERPRETER_PATTERN: PatternCatalogEntry(
        pattern_type=PatternType.INTERPRETER_PATTERN,
        category=PatternCategory.BEHAVIORAL,
        name="Interpreter / DSL Evaluator",
        description="Defining a grammar representation and interpreter evaluation engine for domain-specific language expressions.",
        idiomatic_example="public interface IExpression { int Interpret(Context context); }",
    ),
    PatternType.ITERATOR_YIELD: PatternCatalogEntry(
        pattern_type=PatternType.ITERATOR_YIELD,
        category=PatternCategory.BEHAVIORAL,
        name="Iterator & Generator (yield return)",
        description="Lazy sequential element generation using C# compiler state machines with `yield return`.",
        idiomatic_example="public static IEnumerable<int> GenerateSequence() { while (true) yield return ++count; }",
    ),
    PatternType.MEDIATOR_PATTERN: PatternCatalogEntry(
        pattern_type=PatternType.MEDIATOR_PATTERN,
        category=PatternCategory.BEHAVIORAL,
        name="Mediator / In-Process Message Broker",
        description="Decoupling components by communicating exclusively through a central mediator (MediatR `IMediator`).",
        idiomatic_example="public class OrderController(IMediator mediator) { public Task<IResult> Create(Cmd c) => mediator.Send(c); }",
    ),
    PatternType.MEMENTO_PATTERN: PatternCatalogEntry(
        pattern_type=PatternType.MEMENTO_PATTERN,
        category=PatternCategory.BEHAVIORAL,
        name="Memento / State Snapshot",
        description="Capturing and restoring an object's internal state without violating encapsulation (Undo/Redo stacks).",
        idiomatic_example="public class DocumentStateMemento { public string Content { get; init; } }",
    ),
    PatternType.OBSERVER_EVENT_OBSERVABLE: PatternCatalogEntry(
        pattern_type=PatternType.OBSERVER_EVENT_OBSERVABLE,
        category=PatternCategory.BEHAVIORAL,
        name="Observer / Event / IObservable",
        description="Pub/Sub communication using native C# `event EventHandler<T>`, Reactive Extensions `IObservable<T>`, or `IObserver<T>`.",
        idiomatic_example="public event EventHandler<OrderPlacedEventArgs>? OrderPlaced;",
    ),
    PatternType.STATE_PATTERN: PatternCatalogEntry(
        pattern_type=PatternType.STATE_PATTERN,
        category=PatternCategory.BEHAVIORAL,
        name="State Machine / State Pattern",
        description="Allowing an object to alter its behavior when its internal state changes (State objects or enum state transitions).",
        idiomatic_example="public interface IOrderState { void Process(OrderContext ctx); }",
    ),
    PatternType.STRATEGY_PATTERN: PatternCatalogEntry(
        pattern_type=PatternType.STRATEGY_PATTERN,
        category=PatternCategory.BEHAVIORAL,
        name="Strategy Pattern",
        description="Defining a family of interchangeable algorithms and encapsulating each one behind a common interface.",
        idiomatic_example="public interface IDiscountStrategy { decimal ApplyDiscount(decimal total); }",
    ),
    PatternType.TEMPLATE_METHOD: PatternCatalogEntry(
        pattern_type=PatternType.TEMPLATE_METHOD,
        category=PatternCategory.BEHAVIORAL,
        name="Template Method",
        description="Defining the skeleton of an algorithm in an abstract base class, deferring steps to subclasses via abstract/virtual hooks.",
        idiomatic_example="public abstract class DataExporter { public void Export() { Extract(); Transform(); Save(); } protected abstract void Extract(); }",
    ),
    PatternType.VISITOR_PATTERN: PatternCatalogEntry(
        pattern_type=PatternType.VISITOR_PATTERN,
        category=PatternCategory.BEHAVIORAL,
        name="Visitor Pattern",
        description="Separating an algorithm from an object structure by dispatching operations via `Accept(IVisitor)` double-dispatch.",
        idiomatic_example="public interface IASTVisitor { void Visit(BinaryNode n); void Visit(LiteralNode n); }",
    ),

    # ── 5. Enterprise & .NET Architecture ──────────────────────────────────────
    PatternType.CQRS_MEDIATR_HANDLER: PatternCatalogEntry(
        pattern_type=PatternType.CQRS_MEDIATR_HANDLER,
        category=PatternCategory.ENTERPRISE,
        name="CQRS & MediatR Request Handler",
        description="Command Query Responsibility Segregation separating write commands from read queries via `IRequestHandler<TReq, TRes>`.",
        idiomatic_example="public class GetOrderQueryHandler : IRequestHandler<GetOrderQuery, OrderDto> { ... }",
    ),
    PatternType.REPOSITORY_UNIT_OF_WORK: PatternCatalogEntry(
        pattern_type=PatternType.REPOSITORY_UNIT_OF_WORK,
        category=PatternCategory.ENTERPRISE,
        name="Repository & Unit of Work",
        description="Decoupling domain logic from EF Core DbContext using `IRepository<T>` and `IUnitOfWork.SaveChangesAsync()`.",
        idiomatic_example="public interface IUnitOfWork { IOrderRepository Orders { get; } Task<int> CommitAsync(); }",
    ),
    PatternType.OPTIONS_PATTERN_CONFIGURATION: PatternCatalogEntry(
        pattern_type=PatternType.OPTIONS_PATTERN_CONFIGURATION,
        category=PatternCategory.ENTERPRISE,
        name="Options Pattern Configuration",
        description="Strongly-typed application settings binding with `IOptions<TOptions>`, `IOptionsSnapshot<T>`, or `IOptionsMonitor<T>`.",
        idiomatic_example="public class PaymentService(IOptions<StripeOptions> options) { private readonly StripeOptions _opt = options.Value; }",
    ),
    PatternType.RAILWAY_RESULT_MONAD: PatternCatalogEntry(
        pattern_type=PatternType.RAILWAY_RESULT_MONAD,
        category=PatternCategory.ENTERPRISE,
        name="Railway Result / ErrorOr Monad",
        description="Explicit, type-safe error handling returning `Result<TValue, TError>` or `ErrorOr<T>` instead of throwing exceptions.",
        idiomatic_example="public Result<User> Register(RegisterDto dto) => user.Validate() ? Result.Ok(user) : Result.Fail('Invalid');",
    ),
    PatternType.DEPENDENCY_INJECTION_SERVICE_COLLECTION: PatternCatalogEntry(
        pattern_type=PatternType.DEPENDENCY_INJECTION_SERVICE_COLLECTION,
        category=PatternCategory.ENTERPRISE,
        name="Dependency Injection (IServiceCollection)",
        description="IoC container registration via `AddScoped`, `AddTransient`, `AddSingleton` or extension methods.",
        idiomatic_example="public static IServiceCollection AddInfrastructure(this IServiceCollection services) => services.AddScoped<IUserRepo, UserRepo>();",
    ),

    # ── 6. Concurrency, Channels & TPL ─────────────────────────────────────────
    PatternType.CHANNEL_PRODUCER_CONSUMER: PatternCatalogEntry(
        pattern_type=PatternType.CHANNEL_PRODUCER_CONSUMER,
        category=PatternCategory.CONCURRENCY_ASYNC,
        name="System.Threading.Channels (Actor/Queue)",
        description="High-performance, lock-free async producer-consumer pipeline using `Channel.CreateBounded<T>()`.",
        idiomatic_example="private readonly Channel<Message> _channel = Channel.CreateBounded<Message>(1000);",
    ),
    PatternType.STRUCTURED_TASK_WHEN_ALL: PatternCatalogEntry(
        pattern_type=PatternType.STRUCTURED_TASK_WHEN_ALL,
        category=PatternCategory.CONCURRENCY_ASYNC,
        name="Structured Concurrency (Task.WhenAll)",
        description="Coordinated parallel task execution waiting for multiple async operations via `Task.WhenAll()` or `Task.WhenAny()`.",
        idiomatic_example="await Task.WhenAll(fetchUsersTask, fetchOrdersTask);",
    ),
    PatternType.ASYNC_LOCK_SEMAPHORE: PatternCatalogEntry(
        pattern_type=PatternType.ASYNC_LOCK_SEMAPHORE,
        category=PatternCategory.CONCURRENCY_ASYNC,
        name="Async Synchronization (SemaphoreSlim)",
        description="Non-blocking asynchronous locking across `await` points using `SemaphoreSlim.WaitAsync()`.",
        idiomatic_example="await _semaphore.WaitAsync(); try { ... } finally { _semaphore.Release(); }",
    ),
    PatternType.ASYNC_ENUMERABLE_STREAM: PatternCatalogEntry(
        pattern_type=PatternType.ASYNC_ENUMERABLE_STREAM,
        category=PatternCategory.CONCURRENCY_ASYNC,
        name="Async Streams (IAsyncEnumerable<T>)",
        description="Asynchronous pull-based streaming using `IAsyncEnumerable<T>` and `await foreach` (C# 8+).",
        idiomatic_example="public async IAsyncEnumerable<Event> StreamEventsAsync([EnumeratorCancellation] CancellationToken ct) { ... }",
    ),

    # ── 7. Resilience & Resource Safety ────────────────────────────────────────
    PatternType.SYNC_OVER_ASYNC_DEADLOCK: PatternCatalogEntry(
        pattern_type=PatternType.SYNC_OVER_ASYNC_DEADLOCK,
        category=PatternCategory.RESILIENCE,
        name="Sync-Over-Async Deadlock Hazard",
        description="Blocking on asynchronous tasks using `.Result`, `.Wait()`, or `.GetAwaiter().GetResult()` risking thread-pool starvation.",
        idiomatic_example="var user = GetUserAsync().Result; // HAZARD: Thread-pool exhaustion / deadlock",
    ),
    PatternType.IDISPOSABLE_LEAK_HAZARD: PatternCatalogEntry(
        pattern_type=PatternType.IDISPOSABLE_LEAK_HAZARD,
        category=PatternCategory.RESILIENCE,
        name="IDisposable Unmanaged Resource Leak",
        description="Instantiating `IDisposable` or `IAsyncDisposable` without `using var` declaration risking resource leak.",
        idiomatic_example="var client = new HttpClient(); // Missing 'using var' or shared singleton instance",
    ),
    PatternType.NULL_FORGIVING_SUPPRESSION: PatternCatalogEntry(
        pattern_type=PatternType.NULL_FORGIVING_SUPPRESSION,
        category=PatternCategory.RESILIENCE,
        name="Null-Forgiving Operator Suppression (!)",
        description="Overriding compiler nullability warnings with the null-forgiving operator `!` hiding potential NullReferenceExceptions.",
        idiomatic_example="string name = person.Name!; // HAZARD: runtime NRE if person.Name is actually null",
    ),
    PatternType.TRY_CATCH_BLANKET_SWALLOW: PatternCatalogEntry(
        pattern_type=PatternType.TRY_CATCH_BLANKET_SWALLOW,
        category=PatternCategory.RESILIENCE,
        name="Blanket Exception Swallow",
        description="Catching base `Exception` without rethrowing or logging, silently swallowing critical faults.",
        idiomatic_example="try { Execute(); } catch (Exception) { /* empty */ }",
    ),
    PatternType.MUTABLE_STATIC_FIELD: PatternCatalogEntry(
        pattern_type=PatternType.MUTABLE_STATIC_FIELD,
        category=PatternCategory.RESILIENCE,
        name="Mutable Static State Thread Hazard",
        description="Non-readonly static fields or properties accessible across threads causing data corruption in multi-threaded environments.",
        idiomatic_example="public static List<User> GlobalUsers = new(); // HAZARD: thread race conditions",
    ),

    # ── 8. Principles, Complexity & Quality ────────────────────────────────────
    PatternType.GOD_CLASS_SRP: PatternCatalogEntry(
        pattern_type=PatternType.GOD_CLASS_SRP,
        category=PatternCategory.PRINCIPLE,
        name="God Class (SRP Violation)",
        description="Class exceeding 400 lines of code or centralizing too many disparate responsibilities violating Single Responsibility.",
        idiomatic_example="class UserManager with 30 methods handling DB, emailing, encryption, billing, and UI rendering.",
    ),
    PatternType.CYCLOMATIC_COMPLEXITY_KISS: PatternCatalogEntry(
        pattern_type=PatternType.CYCLOMATIC_COMPLEXITY_KISS,
        category=PatternCategory.PRINCIPLE,
        name="High Cyclomatic Complexity (KISS Violation)",
        description="Method with more than 10 decision points (if/else/switch/catch/loops) making it difficult to test and maintain.",
        idiomatic_example="Deeply nested if-else ladders and multi-level switch blocks.",
    ),
    PatternType.DUPLICATE_CODE_DRY: PatternCatalogEntry(
        pattern_type=PatternType.DUPLICATE_CODE_DRY,
        category=PatternCategory.PRINCIPLE,
        name="Duplicate Code Blocks (DRY Violation)",
        description="Identical or near-identical method signatures and implementation logic duplicated across classes.",
        idiomatic_example="Copy-pasted validation routines or HTTP query serialization logic.",
    ),
    PatternType.CIRCULAR_NAMESPACE_DEPENDENCY: PatternCatalogEntry(
        pattern_type=PatternType.CIRCULAR_NAMESPACE_DEPENDENCY,
        category=PatternCategory.PRINCIPLE,
        name="Circular Namespace / Module Cycle",
        description="Cross-referencing `using` statements between namespaces creating tight bidirectional coupling.",
        idiomatic_example="Namespace A imports Namespace B, while Namespace B imports Namespace A.",
    ),
}
