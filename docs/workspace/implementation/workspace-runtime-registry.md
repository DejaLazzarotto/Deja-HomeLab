# Workspace Runtime Registry

## Status

Implemented

## Phase

W3.4 — Runtime Registry Infrastructure

---

# Overview

The Workspace Runtime Registry introduces the generic infrastructure used by the Workspace Runtime to manage runtime-owned objects.

Its purpose is to eliminate duplicated registry implementations while preserving specialized public APIs.

The registry itself contains no Workspace-specific logic.

It only manages identifiable runtime resources.

---

# Objectives

The Runtime Registry provides:

- generic registration;
- duplicate detection;
- lookup by identifier;
- deterministic ordering;
- immutable snapshots;
- reusable infrastructure for future runtime components.

---

# Architecture

```
WorkspaceRuntime
        │
        │
        ▼
WorkspaceRuntimeExtensionRegistry
        │
        │ uses
        ▼
WorkspaceRuntimeRegistry<T>
```

The specialized registry remains responsible for Workspace-specific behavior while the generic registry provides common storage and lifecycle operations.

---

# Design Principles

## Generic

The infrastructure is completely generic.

Any runtime resource identified by an id can reuse this registry.

---

## Independent

The implementation has no Angular dependency.

No browser dependency.

No UI dependency.

---

## Deterministic

Registries preserve registration order.

Specialized registries may apply additional sorting rules.

---

## Immutable Snapshots

Consumers never receive mutable internal collections.

All public collections are immutable snapshots.

---

# Responsibilities

WorkspaceRuntimeRegistry is responsible for:

- registration
- lookup
- existence checking
- removal
- clearing
- enumeration

It intentionally contains no business logic.

---

# Specialized Registries

Specialized registries extend the generic infrastructure with domain-specific behavior.

Examples include:

- Runtime Extensions
- Runtime Commands
- Runtime Providers
- Runtime Contributions
- Runtime Actions

---

# Runtime Extension Registry

WorkspaceRuntimeExtensionRegistry adds:

- extension point filtering
- owner filtering
- priority ordering
- enabled state
- Workspace-specific exceptions

while delegating storage to WorkspaceRuntimeRegistry.

---

# Runtime Extension Dispatcher

The dispatcher is responsible for:

- locating extensions;
- respecting execution order;
- creating execution context;
- executing synchronous handlers;
- executing asynchronous handlers;
- propagating execution failures.

---

# Runtime Integration

WorkspaceRuntime now owns:

- Runtime Extension Registry
- Runtime Extension Dispatcher

allowing runtime extensions to become first-class runtime resources.

---

# Benefits

The Runtime Registry architecture provides:

- reduced code duplication;
- reusable infrastructure;
- simplified maintenance;
- consistent runtime behavior;
- extensibility for future runtime services.

---

# Future Evolution

The same infrastructure will support:

- Command Registry
- Provider Registry
- Action Registry
- Contribution Registry
- future Runtime services.

This establishes the official reusable runtime infrastructure of the Deja Workspace SDK.