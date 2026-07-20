# Module Configuration API

## Status

Official

## Since

Public Module SDK v1

---

# Purpose

The Module Configuration API allows modules to declare configuration entries that can later be resolved through one or more Configuration Providers.

The API defines configuration contracts.

It does not define where configuration values originate.

---

# Public API

## Register Configuration

```bash
platform_register_module_config \
    "<module>" \
    "<key>" \
    "<default_value>"
```

Registers a configuration entry owned by a module.

### Parameters

| Parameter | Description |
|-----------|-------------|
| module | Module identifier |
| key | Configuration key |
| default_value | Default value used when no provider supplies one |

---

## Get Configuration

```bash
platform_get_module_config \
    "<module>" \
    "<key>"
```

Returns the resolved configuration value.

Resolution is delegated to the Configuration Provider subsystem.

---

## Get Default Value

```bash
platform_get_module_default_config \
    "<module>" \
    "<key>"
```

Returns the default value declared by the module.

---

## Query APIs

### Check configuration

```bash
platform_has_module_config \
    "<module>" \
    "<key>"
```

Returns whether the configuration entry exists.

---

### List module configurations

```bash
platform_list_module_configs \
    "<module>"
```

Returns every configuration declared by the module.

---

### List configured modules

```bash
platform_list_module_configs_modules
```

Returns every module that declares configuration entries.

---

# Registration Lifecycle

Configuration entries must be registered during the Resource Registration stage.

Example:

```bash
platform_module_example_register_resources() {

    platform_register_module_config \
        "example" \
        "cache.enabled" \
        "true"

    platform_register_module_config \
        "example" \
        "cache.ttl" \
        "300"

}
```

---

# Configuration Ownership

Each configuration key belongs to exactly one module.

Only the owning module defines:

- key name;
- default value;
- semantic meaning.

Configuration Providers supply values.

They never define configuration contracts.

---

# Best Practices

- Use descriptive names.
- Group related keys.
- Provide meaningful default values.
- Keep configuration stable across releases.
- Register configuration only during Resource Registration.

---

# Compatibility

This API is part of the Public Module SDK v1.

Its behavior is covered by the SDK compatibility policy.