# Public Module SDK v1

## Status

Official

## Purpose

This document defines the official Public Module SDK of the Deja Platform.

The Public Module SDK is the only supported contract for external module developers.

Everything outside this SDK must be considered implementation detail of the Kernel, even when publicly visible.

---

# SDK Scope

The Public Module SDK v1 is composed exclusively of the following APIs.

| API | Responsibility |
|------|----------------|
| module-command-api | Command registration and execution |
| module-service-api | Service registration and resolution |
| module-extension-api | Extension Points |
| capability-api | Capability registration and execution |
| module-config-api | Module configuration definition |
| module-config-provider-api | Configuration providers |
| module-config-observer-api | Configuration observers |
| manifest-api | Module manifest access |

---

# Public Kernel APIs

The following APIs are public because they are used by the Platform itself.

They are **not part of the Public Module SDK**.

| API | Responsibility |
|------|----------------|
| context-api | Kernel execution context |
| runtime-api | Runtime information |
| metadata-api | Metadata storage |
| dependency-api | Dependency inspection |
| log | Logging utilities |

External modules should avoid depending on these APIs unless explicitly documented.

---

# Internal Kernel Components

The following components are internal implementation details.

They are not supported for external use.

This includes, but is not limited to:

- Dependency Resolver
- Manifest Loader
- Manifest Registry
- Manifest Discovery
- Command Registry
- Command Dispatcher
- Command Loader
- Module Loader
- Lifecycle Manager
- Module State
- Validators
- Internal Registries
- Internal Dispatchers

---

# Compatibility Policy

Only the Public Module SDK is covered by compatibility guarantees.

Internal Kernel components may evolve without notice.

---

# Engineering Rule

Being publicly visible does not automatically make an API part of the SDK.

Only APIs explicitly listed in this document are officially supported for module development.