# Deja Platform Public Module SDK v1

## Status

Official

---

# Overview

The Public Module SDK is the official contract for developing modules for the Deja Platform.

Modules must interact exclusively through the APIs documented by this SDK.

Kernel implementation details are intentionally excluded.

---

# Documentation

## Architecture

- Public Module SDK
- SDK Reference
- Module Development Guide
- Module Lifecycle

---

## Public APIs

- Module Command API
- Module Service API
- Capability API
- Module Extension API
- Module Configuration API
- Module Configuration Provider API
- Module Configuration Observer API

---

# Development Flow

A typical module development workflow is:

1. Create the module structure.
2. Create the module manifest.
3. Implement the module.
4. Register resources.
5. Bootstrap the module.
6. Validate integration.

---

# Public SDK

The SDK provides support for:

- Commands
- Services
- Capabilities
- Extension Points
- Configuration
- Configuration Providers
- Configuration Observers

No other APIs are considered part of the Public Module SDK.

---

# Compatibility

Only APIs documented by this SDK are covered by compatibility guarantees.

Kernel implementation details may change without notice.

---

# References

Architecture documentation:

- ../architecture/platform-philosophy.md
- ../architecture/founding-charter.md
- ../architecture/public-module-sdk.md