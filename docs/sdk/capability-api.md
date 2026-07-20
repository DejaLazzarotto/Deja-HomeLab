# Capability API

## Status

Official

## Since

Public Module SDK v1

---

# Purpose

The Capability API allows modules to publish executable capabilities that can be discovered and invoked through the Kernel.

Capabilities represent functional contracts rather than implementation details.

Unlike Services, Capabilities are intended to expose what a module is able to do, not how it does it.

---

# Public API

## Register Capability

```bash
platform_register_capability \
    "<module>" \
    "<capability>" \
    "<function>"
```

Registers a capability provided by a module.

### Parameters

| Parameter | Description |
|-----------|-------------|
| module | Module identifier |
| capability | Capability name |
| function | Function implementing the capability |

---

## Execute Capability

```bash
platform_execute_capability "<capability>" [arguments...]
```

Executes the registered capability.

The execution result is returned directly by the implementation.

---

## Query APIs

### Check existence

```bash
platform_has_capability "<capability>"
```

Returns whether a capability exists.

---

### Get provider

```bash
platform_get_capability_provider "<capability>"
```

Returns the module that registered the capability.

---

### List capabilities

```bash
platform_list_capabilities
```

Returns every registered capability.

---

# Registration Lifecycle

Capabilities must be registered during the Resource Registration stage.

Example:

```bash
platform_module_example_register_resources() {
    platform_register_capability \
        "example" \
        "example.compress" \
        "platform_example_compress"
}
```

---

# Capability Design

Capabilities should represent stable functional contracts.

Consumers should depend on the capability name rather than on the implementing module.

Capability implementations remain private to the provider module.

---

# Best Practices

- Use globally unique capability names.
- Keep capabilities focused on a single responsibility.
- Avoid exposing implementation details.
- Register capabilities only during Resource Registration.
- Do not replace capabilities registered by other modules.

---

# Services vs Capabilities

| Services | Capabilities |
|----------|--------------|
| Represent reusable implementations | Represent executable functionality |
| Usually resolved before invocation | Invoked directly |
| Emphasize provider contracts | Emphasize functional behavior |

---

# Compatibility

This API is part of the Public Module SDK v1.

Its behavior is covered by the SDK compatibility policy.