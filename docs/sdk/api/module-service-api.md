# Module Service API

## Status

Official

## Since

Public Module SDK v1

---

# Purpose

The Module Service API allows modules to publish reusable services that can be resolved and consumed by other modules.

Services provide the primary mechanism for collaboration between modules while preserving loose coupling.

---

# Public API

## Register Service

```bash
platform_register_service \
    "<module>" \
    "<service>" \
    "<function>"
```

Registers a service implementation.

### Parameters

| Parameter | Description |
|-----------|-------------|
| module | Module identifier |
| service | Unique service name |
| function | Function implementing the service |

---

## Resolve Service

```bash
platform_resolve_service "<service>"
```

Returns the function associated with the service.

---

## Query APIs

### Check existence

```bash
platform_has_service "<service>"
```

Returns whether a service is registered.

---

### Get provider

```bash
platform_get_service_provider "<service>"
```

Returns the module that registered the service.

---

### List services

```bash
platform_list_services
```

Returns all registered services.

---

# Registration Lifecycle

Services must be registered during the Resource Registration stage.

Example:

```bash
platform_module_example_register_resources() {
    platform_register_service \
        "example" \
        "example.storage" \
        "platform_example_storage_service"
}
```

---

# Service Design

A service should expose a stable and well-defined contract.

Consumers should depend only on the service contract, never on the implementation details of the providing module.

---

# Best Practices

- Use globally unique service names.
- Prefer a single responsibility per service.
- Keep implementations private to the module.
- Avoid service registration outside Resource Registration.
- Do not overwrite services registered by other modules.

---

# Compatibility

This API is part of the Public Module SDK v1.

Its behavior is covered by the SDK compatibility policy.