# ADR-001 — Runtime Registry Architecture

## Status

Accepted

---

## Date

2026-07-22

---

## Context

The initial Workspace Runtime implementation introduced specialized registries for Runtime Extensions.

Although functional, the implementation duplicated generic registry behavior such as:

- registration;
- duplicate detection;
- lookup;
- removal;
- enumeration.

As additional runtime components (Commands, Providers, Actions and Contributions) were planned, maintaining separate implementations would increase maintenance cost and reduce consistency.

---

## Decision

Introduce a generic infrastructure named **WorkspaceRuntimeRegistry<T>**.

The generic registry becomes the official reusable storage layer for runtime-managed resources.

Specialized registries remain responsible only for Workspace-specific behavior.

---

## Architecture

```
WorkspaceRuntime
        │
        ▼
WorkspaceRuntimeExtensionRegistry
        │
        ▼
WorkspaceRuntimeRegistry<T>
```

The specialized registry delegates generic storage operations to the generic registry.

---

## Why Composition

Composition was intentionally selected instead of inheritance.

Reasons:

- preserve public API stability;
- hide implementation details;
- prevent leakage of generic exceptions;
- allow specialized registries to expose Workspace-specific contracts;
- simplify future evolution.

---

## Consequences

Positive:

- reduced duplicated code;
- consistent runtime behavior;
- reusable infrastructure;
- easier testing;
- lower maintenance cost;
- easier future extensions.

Trade-offs:

- one additional abstraction layer;
- specialized registries remain necessary.

The trade-off is considered acceptable because it preserves a clean public SDK.

---

## Future Impact

The same infrastructure will be reused by:

- Workspace Command Registry
- Workspace Provider Registry
- Workspace Action Registry
- Workspace Contribution Registry
- future Runtime services.

---

## Decision Summary

The Workspace SDK officially adopts a reusable Runtime Registry architecture based on generic infrastructure and specialized composition-based registries.

This decision becomes part of the permanent architectural foundation of the Deja Workspace SDK.