# Module Extension API

## Status

Official

## Since

Public Module SDK v1

---

# Purpose

The Module Extension API allows modules to extend platform behavior through well-defined Extension Points.

Extension Points enable extensibility without creating direct dependencies between modules.

The Kernel owns Extension Points.

Modules provide Extension Providers.

---

# Public API

## Register Extension Point

```bash
platform_register_extension_point \
    "<extension_point>"
```

Registers a new Extension Point.

Extension Points should normally be created by infrastructure modules.

---

## Register Extension Provider

```bash
platform_register_extension_provider \
    "<module>" \
    "<extension_point>" \
    "<function>"
```

Registers a provider for an Extension Point.

### Parameters

| Parameter | Description |
|-----------|-------------|
| module | Module identifier |
| extension_point | Extension Point name |
| function | Provider implementation |

---

## Execute Extension

```bash
platform_execute_extension "<extension_point>" [arguments...]
```

Executes the provider registered for the Extension Point.

The execution result is returned by the provider.

---

## Query APIs

### Check Extension Point

```bash
platform_has_extension_point "<extension_point>"
```

Returns whether an Extension Point exists.

---

### Check Provider

```bash
platform_has_extension_provider "<extension_point>"
```

Returns whether an Extension Point has a registered provider.

---

### Get Provider

```bash
platform_get_extension_provider "<extension_point>"
```

Returns the module providing the Extension Point.

---

### List Extension Points

```bash
platform_list_extension_points
```

Returns all registered Extension Points.

---

### List Providers

```bash
platform_list_extension_providers
```

Returns all registered Extension Providers.

---

# Registration Lifecycle

Extension Points and Extension Providers must be registered during the Resource Registration stage.

Example:

```bash
platform_module_example_register_resources() {

    platform_register_extension_provider \
        "example" \
        "kernel.authentication" \
        "platform_example_auth_provider"

}
```

---

# Extension Design

Extension Points define contracts.

Providers implement contracts.

Consumers execute contracts.

Neither consumers nor providers should depend on each other directly.

---

# Best Practices

- Use globally unique Extension Point names.
- Keep Extension Point contracts stable.
- Register providers only during Resource Registration.
- Keep provider implementations private.
- Avoid implementation-specific assumptions.

---

# Extension Point Ownership

The module that creates an Extension Point owns its contract.

Provider modules must comply with the contract defined by the owner.

---

# Compatibility

This API is part of the Public Module SDK v1.

Its behavior is covered by the SDK compatibility policy.