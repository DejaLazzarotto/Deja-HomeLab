# Manifest API

## Status

Official

## Since

Public Module SDK v1

---

# Purpose

The Manifest API provides access to the public metadata of registered modules.

It allows modules to inspect manifest fields, versions, API compatibility, entrypoints, dependencies, activation state and physical module directories.

The API also exposes manifest registration operations used by the platform module-loading flow.

---

# Public Manifest Fields

The following manifest fields may be accessed through the Public Module SDK:

| Field          | Description                                       |
| -------------- | ------------------------------------------------- |
| `name`         | Module identifier.                                |
| `version`      | Module version.                                   |
| `description`  | Human-readable module description.                |
| `author`       | Module author or maintainer.                      |
| `api_version`  | Public Module SDK version required by the module. |
| `entrypoint`   | Module entrypoint file.                           |
| `dependencies` | Declared module dependencies.                     |
| `enabled`      | Whether the module is enabled.                    |

Fields not included in this list are not part of the public manifest contract.

---

# Public Functions

## `platform_get_module_manifest_field()`

Returns a public manifest field for a registered module.

```bash
platform_get_module_manifest_field <module> <field>
```

Example:

```bash
platform_get_module_manifest_field "example" "description"
```

---

## `platform_get_module_version()`

Returns the version declared by a module.

```bash
platform_get_module_version <module>
```

Example:

```bash
platform_get_module_version "example"
```

---

## `platform_get_module_api_version()`

Returns the Public Module SDK version declared by a module.

```bash
platform_get_module_api_version <module>
```

Example:

```bash
platform_get_module_api_version "example"
```

---

## `platform_get_module_entrypoint()`

Returns the entrypoint declared by a module.

```bash
platform_get_module_entrypoint <module>
```

Example:

```bash
platform_get_module_entrypoint "example"
```

---

## `platform_get_module_dependencies()`

Returns the dependencies declared by a module.

```bash
platform_get_module_dependencies <module>
```

Example:

```bash
platform_get_module_dependencies "example"
```

---

## `platform_is_module_enabled()`

Checks whether a registered module is enabled.

```bash
platform_is_module_enabled <module>
```

Return status:

| Status | Meaning                                         |
| ------ | ----------------------------------------------- |
| `0`    | The module is enabled.                          |
| `1`    | The module is disabled or the operation failed. |

Example:

```bash
if platform_is_module_enabled "example"; then
    echo "Module is enabled."
fi
```

---

## `platform_list_registered_manifests()`

Lists the modules whose manifests are currently registered.

```bash
platform_list_registered_manifests
```

---

## `platform_register_module_manifest()`

Registers a module manifest.

```bash
platform_register_module_manifest \
    <name> \
    <version> \
    <description> \
    <author> \
    <api_version> \
    <entrypoint> \
    <dependencies> \
    <enabled> \
    <manifest_file> \
    <module_directory>
```

This operation is normally performed by the platform module-loading flow.

External modules should not register their own manifest during resource registration or bootstrap.

---

## `platform_is_module_manifest_registered()`

Checks whether a module manifest is registered.

```bash
platform_is_module_manifest_registered <module>
```

Example:

```bash
if platform_is_module_manifest_registered "example"; then
    echo "Manifest is registered."
fi
```

---

## `platform_get_module_directory()`

Returns the physical directory of a registered module.

```bash
platform_get_module_directory <module>
```

Example:

```bash
module_directory="$(platform_get_module_directory "example")" || return 1
```

---

# Usage Rules

Modules should use the Manifest API only to inspect public module metadata.

Modules must not access:

* the Manifest Registry directly;
* manifest loader internals;
* manifest discovery internals;
* private registry fields;
* Kernel storage structures.

Manifest registration is part of the platform loading mechanism and should not be repeated by module implementations.

---

# Compatibility

The functions and manifest fields documented here are part of the Public Module SDK v1 compatibility contract.

Undocumented manifest fields and internal Manifest Registry operations are not covered by compatibility guarantees.
