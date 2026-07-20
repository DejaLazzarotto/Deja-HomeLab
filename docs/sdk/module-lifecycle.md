# Module Lifecycle

## Status

Official

## Since

Public Module SDK v1

---

# Purpose

This document defines the official lifecycle of modules in the Deja Platform.

The lifecycle is managed entirely by the Kernel.

Modules must never attempt to control or bypass lifecycle execution.

---

# Lifecycle Stages

The Kernel executes the following stages for every module.

```
Manifest Discovery
        │
        ▼
Manifest Validation
        │
        ▼
Dependency Resolution
        │
        ▼
Module Loading
        │
        ▼
Resource Registration
        │
        ▼
Bootstrap
```

Each stage is executed exactly once.

---

# Manifest Discovery

The Kernel locates every module manifest.

No module code is executed during this stage.

---

# Manifest Validation

Each manifest is validated before the module is accepted.

Invalid modules do not continue through the lifecycle.

---

# Dependency Resolution

Dependencies are resolved before loading modules.

Bootstrap order is determined by the dependency graph.

Modules must never assume filesystem loading order.

---

# Module Loading

The Kernel loads the module implementation.

Loading must not produce observable side effects.

---

# Resource Registration

After loading, the Kernel invokes:

```bash
platform_module_<module>_register_resources
```

The module publishes its resources to the Kernel.

Typical resources include:

- Commands
- Services
- Capabilities
- Extension Providers
- Configuration Providers
- Configuration Observers

Resource registration should never execute business logic.

---

# Bootstrap

After every resource has been registered, the Kernel invokes:

```bash
platform_module_<module>_bootstrap
```

Bootstrap initializes runtime behavior.

Resources are expected to be fully available.

---

# Lifecycle Guarantees

The Kernel guarantees:

- deterministic execution order;
- dependency-aware bootstrap;
- resource registration before bootstrap;
- a module is bootstrapped at most once;
- failed modules do not prevent unrelated modules from being processed unless dependency rules require it.

---

# Module Responsibilities

A module must:

- expose a valid manifest;
- publish its resources during resource registration;
- initialize runtime during bootstrap;
- communicate only through the Public Module SDK.

---

# Forbidden Behaviors

Modules must not:

- invoke lifecycle stages directly;
- manipulate lifecycle state;
- register resources after bootstrap;
- access internal lifecycle managers.

---

# Compatibility

The lifecycle described in this document is part of the Public Module SDK v1 contract.

Kernel implementations may evolve internally provided this observable behavior remains unchanged.