# Module Development Guide

## Status

Official

## Since

Public Module SDK v1

---

# Introduction

A module is the primary extension unit of the Deja Platform.

Modules provide behavior.

The Kernel provides mechanisms.

This separation is one of the fundamental architectural principles of the platform.

---

# Minimal Module Structure

```
modules/
└── example/
    ├── module.sh
    ├── manifest.yaml
    ├── commands/
    ├── services/
    ├── extensions/
    └── config/
```

Only `module.sh` and `manifest.yaml` are mandatory.

The remaining directories exist only when required by the module.

---

# Module Responsibilities

A module may provide:

- Commands
- Services
- Capabilities
- Extension Providers
- Configuration Definitions
- Configuration Observers

A module is not required to provide all of them.

---

# Module Bootstrap

The Kernel performs the bootstrap.

Modules only publish resources.

The lifecycle is:

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

Each stage has a single responsibility.

---

# Resource Registration

Resources must be registered through:

```bash
platform_module_<module>_register_resources()
```

This function is called automatically by the Kernel.

Typical registrations include:

- Commands
- Services
- Capabilities
- Extension Providers
- Configuration Providers
- Configuration Observers

No business logic should be executed during resource registration.

---

# Bootstrap

After resource registration the Kernel invokes:

```bash
platform_module_<module>_bootstrap()
```

Bootstrap should initialize runtime behavior only.

Resources should already be registered.

---

# Module Independence

Modules should communicate exclusively through the Public Module SDK.

Modules must never access:

- internal registries;
- internal dispatchers;
- Kernel storage;
- global implementation details.

---

# Allowed Dependencies

Modules may depend only on:

- Public Module SDK
- Public Module Manifest
- Official lifecycle

Everything else must be considered internal.

---

# Engineering Principles

A module should:

- expose a single responsibility;
- publish only its own resources;
- remain deterministic;
- avoid hidden side effects;
- avoid global mutable state.

---

# Compatibility

Modules that depend exclusively on the Public Module SDK are covered by the SDK compatibility policy.