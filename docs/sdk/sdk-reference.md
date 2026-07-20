# Deja Platform SDK Reference

## Status

Official

---

# Purpose

This document is the official entry point for the Deja Platform Public Module SDK.

It provides a complete map of every public API available to module developers.

Only the APIs listed here are considered part of the stable SDK contract.

---

# Public Module SDK

## Architecture

| Document | Description | Reference |
|----------|-------------|-----------|
| Public Module SDK | Defines the official SDK scope | `../architecture/public-module-sdk.md` |
| SDK Reference | Complete map of the Public Module SDK | `sdk-reference.md` |
| Module Development Guide | Official guide for module developers | `guides/module-development-guide.md` |
| Module Lifecycle | Official module lifecycle | `guides/module-lifecycle.md` |

---

## Public APIs

| API | Responsibility | Reference |
|-----|----------------|-----------|
| Module Command API | Register module commands | `api/module-command-api.md` |
| Module Service API | Register module services | `api/module-service-api.md` |
| Capability API | Register capabilities | `api/capability-api.md` |
| Module Extension API | Register extension points | `api/module-extension-api.md` |
| Module Configuration API | Access module configuration | `api/module-config-api.md` |
| Module Configuration Provider API | Register configuration providers | `api/module-config-provider-api.md` |
| Module Configuration Observer API | Observe configuration events | `api/module-config-observer-api.md` |

---

# Compatibility

Every API listed in this document is covered by the Public Module SDK compatibility guarantees.

Any symbol not documented here must be considered internal.

---

# Stability

Kernel internals may evolve over time.

Only the Public Module SDK remains stable across compatible platform versions.

---

# Next References

This document is complemented by:

- Module Development Guide
- Module Lifecycle
- Individual API references
- Official module examples

---

# Public API Map

The following sections define every public function officially supported by the Deja Platform Public Module SDK v1.

Only the symbols documented below are considered part of the stable SDK contract.

---

# Module Command API

Purpose:

Register commands exposed by a module.

Public functions:

| Function | Description |
|----------|-------------|
| `platform_register_module_command()` | Registers a module command. |
| `platform_unregister_module_command()` | Unregisters a module command. |
| `platform_list_module_commands()` | Lists registered module commands. |
| `platform_module_command_exists()` | Checks whether a command exists. |
| `platform_get_module_command_description()` | Returns a command description. |
| `platform_get_module_command_origin()` | Returns the module that owns the command. |

---

# Module Service API

Purpose:

Register services exposed by a module for consumption by other modules.

Public functions:

| Function | Description |
|----------|-------------|
| `platform_register_module_service()` | Registers a module service. |
| `platform_unregister_module_service()` | Unregisters a module service. |
| `platform_list_module_services()` | Lists registered module services. |
| `platform_module_service_exists()` | Checks whether a service exists. |
| `platform_get_module_service()` | Returns the implementation associated with a service. |
| `platform_get_module_service_module()` | Returns the module that owns a service. |

---

# Capability API

Purpose:

Register capabilities exposed by modules.

Public functions:

| Function | Description |
|----------|-------------|
| `platform_register_module_capability()` | Registers a module capability. |
| `platform_unregister_module_capability()` | Unregisters a module capability. |
| `platform_list_module_capabilities()` | Lists registered capabilities. |
| `platform_module_capability_exists()` | Checks whether a capability exists. |
| `platform_get_module_capability()` | Returns the provider associated with a capability. |
| `platform_get_module_capability_module()` | Returns the module that owns a capability. |

---

# Module Extension API

Purpose:

Register extension points and provide implementations for extension points published by other modules.

Public functions:

| Function | Description |
|----------|-------------|
| `platform_register_module_extension()` | Registers an extension provider for an extension point. |
| `platform_unregister_module_extension()` | Unregisters an extension provider. |
| `platform_list_module_extensions()` | Lists registered extension points. |
| `platform_module_extension_exists()` | Checks whether an extension point has a registered provider. |
| `platform_execute_module_extension()` | Executes the provider registered for an extension point. |
| `platform_get_module_extension_provider()` | Returns the provider associated with an extension point. |

---

# Module Configuration API

Purpose:

Access configuration values provided by the platform configuration system.

Public functions:

| Function | Description |
|----------|-------------|
| `platform_get_module_config()` | Returns the complete configuration for a module. |
| `platform_get_module_default_config()` | Returns the default configuration for a module. |
| `platform_context_get()` | Returns a value from the platform context. |
| `platform_context_has()` | Checks whether a context entry exists. |
| `platform_context_get_value()` | Returns a specific value from a context namespace. |
| `platform_context_has_value()` | Checks whether a value exists inside a context namespace. |

---

# Module Configuration Provider API

Purpose:

Register configuration providers that supply configuration data to the platform.

Public functions:

| Function | Description |
|----------|-------------|
| `platform_register_module_config_provider()` | Registers a configuration provider. |
| `platform_unregister_module_config_provider()` | Unregisters a configuration provider. |
| `platform_list_module_config_providers()` | Lists registered configuration providers. |
| `platform_module_config_provider_exists()` | Checks whether a configuration provider exists. |
| `platform_get_module_config_provider()` | Returns the implementation associated with a configuration provider. |
| `platform_get_module_config_provider_module()` | Returns the module that owns a configuration provider. |

---

# Module Configuration Observer API

Purpose:

Register observers that react to configuration lifecycle events emitted by the platform.

Public functions:

| Function | Description |
|----------|-------------|
| `platform_register_module_config_observer()` | Registers a configuration observer. |
| `platform_unregister_module_config_observer()` | Unregisters a configuration observer. |
| `platform_list_module_config_observers()` | Lists registered configuration observers. |
| `platform_module_config_observer_exists()` | Checks whether a configuration observer exists. |
| `platform_get_module_config_observer()` | Returns the callback associated with a configuration observer. |
| `platform_get_module_config_observer_module()` | Returns the module that owns a configuration observer. |