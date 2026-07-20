# Module Configuration Provider API

## Status

Official

## Since

Public Module SDK v1

---

# Purpose

The Module Configuration Provider API allows the Kernel to resolve configuration values from different sources.

Configuration Providers implement the resolution mechanism.

They do not define configuration contracts.

---

# Public API

## Register Configuration Provider

```bash
platform_register_module_config_provider \
    "<provider>" \
    "<resolver_function>"
```

Registers a Configuration Provider.

### Parameters

| Parameter | Description |
|-----------|-------------|
| provider | Provider identifier |
| resolver_function | Function responsible for resolving configuration values |

---

## Resolve Configuration

```bash
platform_resolve_module_config \
    "<module>" \
    "<key>"
```

Resolves the value using the default provider chain.

---

## Resolve Using Specific Provider

```bash
platform_resolve_module_config_with_provider \
    "<provider>" \
    "<module>" \
    "<key>"
```

Resolves the value using a specific provider.

---

## Query APIs

### Check provider

```bash
platform_has_module_config_provider \
    "<provider>"
```

Returns whether a provider is registered.

---

### List providers

```bash
platform_list_module_config_providers
```

Returns all registered Configuration Providers.

---

# Registration Lifecycle

Configuration Providers must be registered during the Resource Registration stage.

Example:

```bash
platform_module_example_register_resources() {

    platform_register_module_config_provider \
        "example" \
        "platform_example_config_provider"

}
```

---

# Provider Responsibilities

A Configuration Provider is responsible only for obtaining configuration values.

Examples include:

- YAML files
- Environment variables
- Databases
- Remote configuration services
- Secret managers

The provider must not define configuration semantics.

---

# Provider Resolution

The Kernel determines which provider is used.

Modules should request configuration values through the public API rather than invoking providers directly.

---

# Best Practices

- Keep providers deterministic.
- Avoid side effects.
- Return values compatible with the declared configuration contract.
- Do not modify configuration definitions.
- Keep provider implementations private.

---

# Compatibility

This API is part of the Public Module SDK v1.

Its behavior is covered by the SDK compatibility policy.