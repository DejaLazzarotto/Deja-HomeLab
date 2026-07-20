# Arquitetura Oficial de Módulos

## Status

Official

## Since

Public Module SDK v1

## Purpose

This document defines the official architecture for modules in the Deja Platform.

It establishes the physical organization, architectural responsibilities, lifecycle integration and development conventions required for modules built on the Public Module SDK v1.

The Kernel implementation is the single source of truth for this specification.

---

# Module Architecture Philosophy

Modules are the fundamental unit of extensibility in the Deja Platform.

Every feature provided by the platform is expected to be implemented as a module following the contracts defined by the Public Module SDK.

A module is an isolated software component that contributes resources to the platform through stable public APIs. Modules never modify Kernel internals directly. Instead, they integrate with the platform by registering resources during the Resource Registration stage and participating in the official module lifecycle.

This architectural model provides:

- predictable bootstrap behavior;
- deterministic dependency resolution;
- clear separation between Kernel and modules;
- stable public contracts;
- independent evolution of platform features;
- long-term compatibility between modules and the Kernel.

The physical organization of a module is not merely a directory layout. It represents the architectural contract between module authors and the Kernel.

For this reason, every official module should follow the conventions defined in this document.

The Kernel implementation defines the module architecture. Documentation formalizes that architecture without extending or modifying it.

---

# Official Module Structure

Every module shall follow the official directory structure defined by the Deja Platform.

The Kernel discovers, loads and bootstraps modules assuming a consistent physical organization. Maintaining this structure ensures compatibility with the Public Module SDK and allows the platform to evolve without requiring changes to existing modules.

The following tree represents the complete reference structure for an official module.

```text
module-name/
├── module.conf
├── module.sh
│
├── commands/
│
├── services/
│
├── capabilities/
│
├── extensions/
│
├── providers/
│
├── observers/
│
├── config/
│
├── docs/
│
├── examples/
│
└── tests/
```

Not every directory is mandatory.

Only the files required by the Kernel must always exist. All other directories are optional and should be created only when the module provides the corresponding resources.

Empty directories are discouraged.

A module should expose only the resources that it actually implements.

---

# Required Files

Every official module shall contain the following files.

| File | Required | Purpose |
|------|----------|----------|
| module.conf | Yes | Module metadata and manifest definition |
| module.sh | Yes | Module entry point |

These files are required for every module recognized by the Kernel.

A module missing one of these files is considered structurally invalid and is not compliant with the Public Module SDK.

The contents of these files are defined by the official Module Manifest and Module Entry Point specifications.

---

# Optional Directories

The remaining directories are optional.

They should be created only when the module implements the corresponding resource.

| Directory | Purpose |
|-----------|---------|
| commands/ | CLI commands exposed by the module |
| services/ | Internal service implementations |
| capabilities/ | Capability implementations |
| extensions/ | Extension points and extension providers |
| providers/ | Configuration providers |
| observers/ | Configuration observers |
| config/ | Module configuration files |
| docs/ | Module documentation |
| examples/ | Usage examples |
| tests/ | Automated tests |

The absence of an optional directory does not affect module validity.

Modules should contain only the directories required by their implementation.

This principle keeps modules simple, self-contained and easy to maintain.

---

# Directory Responsibilities

Each directory defined by the official module structure has a single architectural responsibility.

Modules should organize their implementation according to these responsibilities.

## commands/

Contains the implementations of the CLI commands exposed by the module.

Each command should be implemented independently and registered during the Resource Registration stage.

---

## services/

Contains the internal service implementations provided by the module.

Services encapsulate reusable business logic that can be consumed through the Module Service Public API.

---

## capabilities/

Contains capability implementations exported by the module.

Capabilities provide well-defined functionality that may be executed by other modules through the Capability API.

---

## extensions/

Contains extension-related resources.

This directory may contain:

- Extension Point definitions;
- Extension Provider implementations.

Extension Points define where other modules may integrate.

Extension Providers implement behavior for existing Extension Points.

---

## providers/

Contains Configuration Provider implementations.

Configuration Providers resolve configuration values requested through the Module Configuration Public API.

---

## observers/

Contains Configuration Observer implementations.

Observers receive configuration lifecycle notifications generated by the Kernel.

---

## config/

Contains module configuration files.

The organization and format of these files are defined by the Configuration subsystem.

---

## docs/

Contains documentation specific to the module.

Documentation stored here complements the official SDK documentation and should describe module-specific behavior.

---

## examples/

Contains reference examples demonstrating how to use the module.

Examples are intended for module consumers and developers.

---

## tests/

Contains automated tests related to the module.

Tests should validate the behavior of the module without depending on Kernel implementation details.

---

# Naming Conventions

Official modules shall follow the naming conventions defined in this section.

Consistent naming improves readability, predictability and interoperability across the platform.

---

## Module Identifier

Every module shall have a unique identifier.

Module identifiers should:

- use lowercase letters;
- use hyphens (`-`) to separate words;
- avoid spaces;
- avoid underscores;
- remain stable throughout the lifetime of the module.

Examples:

```text
core
database
yaml-config
http-server
audit-hook
```

The module identifier is defined in `module.conf`.

---

## Directory Names

Official directory names are fixed by the module architecture and shall not be renamed.

```text
commands/
services/
capabilities/
extensions/
providers/
observers/
config/
docs/
examples/
tests/
```

---

## Script Files

Script filenames should:

- use lowercase letters;
- use hyphens to separate words;
- describe a single responsibility.

Examples:

```text
status.sh
health-check.sh
yaml-provider.sh
config-observer.sh
```

---

## Shell Functions

Functions exposed by a module should use the following prefix:

```text
platform_module_<module>_
```

Examples:

```text
platform_module_core_bootstrap
platform_module_database_register_resources
platform_module_yaml_register_providers
```

Functions intended to implement commands should use descriptive names consistent with the command they execute.

Examples:

```text
platform_cmd_core_status
platform_cmd_database_migrate
```

---

## Public Resource Identifiers

Commands, services, capabilities and extension points should use clear, descriptive and stable identifiers.

Identifiers should avoid abbreviations unless they are already established within the platform.

Public identifiers are considered part of the module contract and should remain stable across compatible releases.

---

# Module Entry Point (module.sh)

Every official module shall provide a `module.sh` file.

This file is the module entry point recognized by the Kernel.

Its responsibility is to expose the functions that integrate the module with the official module lifecycle.

The entry point should not contain business logic.

Instead, it should coordinate resource registration and bootstrap by delegating implementation to the appropriate module components.

The functions exposed by `module.sh` participate in the official lifecycle managed by the Kernel.

Typical responsibilities include:

- registering Commands;
- registering Services;
- registering Capabilities;
- registering Extension Points;
- registering Extension Providers;
- registering Configuration Providers;
- registering Configuration Observers;
- performing module bootstrap.

The exact set of functions implemented by a module depends on the resources it provides.

Modules should not implement lifecycle functions that have no purpose.

Unused lifecycle functions should be omitted.

The Kernel invokes lifecycle functions according to the module lifecycle specification.

Module authors should never invoke these functions directly.

---

# Module Manifest (module.conf)

Every official module shall provide a `module.conf` file.

The module manifest is the authoritative source of metadata describing the module to the Kernel.

During the Discovery stage, the Kernel reads the manifest to identify the module and determine the information required for dependency resolution and module loading.

The manifest does not contain executable logic.

Its responsibility is limited to declaring module metadata and configuration required by the official module lifecycle.

The format and supported fields of the manifest are defined by the official Module Manifest specification.

Module authors should not introduce custom fields that modify Kernel behavior unless explicitly supported by the Public Module SDK.

The module manifest is considered part of the public contract between the module and the Kernel.

Its contents should remain stable across compatible releases.

---

# Resource Organization

Resources are the mechanisms through which a module integrates with the Deja Platform.

Every resource published by a module shall be registered through the corresponding Public Module SDK API during the Resource Registration stage.

Resources should remain independent from one another whenever possible.

A module may implement any combination of supported resources according to its responsibilities.

The following sections define the official organization for each resource type supported by the Public Module SDK.

## Commands

Commands expose functionality through the Deja Platform CLI.

Command implementations should be placed inside the `commands/` directory.

Each command should have a single responsibility.

Commands shall be registered during the Resource Registration stage using the Module Command Public API.

The implementation of a command should remain independent from the module entry point.

The `module.sh` file is responsible only for registering the command with the Kernel.

## Services

Services encapsulate reusable functionality provided by a module.

Service implementations should be placed inside the `services/` directory.

Services are intended for programmatic consumption by other modules through the Module Service Public API.

Each service should expose a well-defined responsibility.

Services shall be registered during the Resource Registration stage.

The module entry point is responsible only for registering the service.

Business logic should remain inside the service implementation.

## Capabilities

Capabilities expose executable functionality that may be invoked by other modules.

Capability implementations should be placed inside the `capabilities/` directory.

Capabilities shall be registered during the Resource Registration stage using the Capability Public API.

Each capability should represent a single functional responsibility.

Capability implementations should remain independent from lifecycle management.

The Kernel is responsible for capability discovery and execution.

## Extension Points

Extension Points define official integration locations within a module.

An Extension Point allows other modules to contribute additional behavior without modifying the module implementation.

Extension Point definitions should be organized inside the `extensions/` directory.

Extension Points shall be registered during the Resource Registration stage.

Only stable integration contracts should be exposed as Extension Points.

Changes to an Extension Point may affect compatibility with existing modules and should therefore be considered part of the module's public contract.

## Extension Providers

Extension Providers implement behavior for an existing Extension Point.

Extension Provider implementations should be placed inside the `extensions/` directory.

Providers shall be registered during the Resource Registration stage using the Extension Public API.

A provider should implement only the behavior associated with a single Extension Point.

Extension Providers should not depend on Kernel internals.

Their interaction with the platform shall occur exclusively through the Public Module SDK.

## Configuration Providers

Configuration Providers are responsible for resolving configuration values requested by the platform.

Provider implementations should be placed inside the `providers/` directory.

Providers shall be registered during the Resource Registration stage using the Module Configuration Public API.

Each provider should implement a single configuration source.

Configuration Providers should resolve configuration values only.

They should not modify platform state or perform module initialization.

## Configuration Observers

Configuration Observers receive notifications generated by the Configuration subsystem.

Observer implementations should be placed inside the `observers/` directory.

Observers shall be registered during the Resource Registration stage.

Observers may react to configuration lifecycle events, such as loading, invalidation and refresh operations.

Configuration Observers should not replace Configuration Providers.

Their responsibility is limited to reacting to configuration events generated by the Kernel.

## Module Documentation

Documentation specific to a module should be placed inside the `docs/` directory.

Module documentation complements the official SDK documentation.

It should describe module-specific behavior, usage examples and implementation details that are relevant to module consumers.

Documentation should not redefine Public Module SDK contracts.

The official SDK documentation remains the authoritative source for platform behavior.

## Module Tests

Automated tests should be placed inside the `tests/` directory.

Tests should validate the observable behavior of the module.

Whenever possible, tests should exercise the module through the Public Module SDK rather than relying on Kernel implementation details.

Module tests should remain isolated and deterministic.

A module should not depend on the presence of unrelated modules in order to validate its own behavior.

---

# Discovery Flow

Module Discovery is the first stage of the official module lifecycle.

During this stage, the Kernel scans the configured module directories searching for valid module manifests.

The Discovery stage has the following responsibilities:

- locate candidate modules;
- identify module manifests;
- validate the physical structure required for discovery;
- collect module metadata.

Discovery does not load modules.

Discovery does not execute module code.

Discovery does not register resources.

The only output of this stage is the list of discovered modules and their corresponding metadata.

After all modules have been discovered, the Kernel proceeds to dependency resolution.

---

# Loading Flow

The Loading stage begins after dependency resolution has been completed successfully.

Modules are loaded according to the dependency graph produced by the Kernel.

During this stage, the Kernel:

- loads the module entry point;
- prepares the module for execution;
- updates the module lifecycle state.

Loading does not execute bootstrap logic.

Loading does not register resources.

Loading only makes the module implementation available to the Kernel.

Modules are expected to expose the lifecycle functions required by the Resource Registration and Bootstrap stages.

---

# Resource Registration Flow

Resource Registration is the stage where modules publish their resources to the platform.

Once a module has been loaded, the Kernel invokes the module resource registration function.

During this stage, modules may register:

- Commands;
- Services;
- Capabilities;
- Extension Points;
- Extension Providers;
- Configuration Providers;
- Configuration Observers.

Only resource registration should occur during this stage.

Modules should not perform business initialization during Resource Registration.

Resource Registration is responsible for making module resources available to the rest of the platform before bootstrap begins.

---

# Bootstrap Flow

Bootstrap is the final stage of the official module lifecycle.

After all resources have been registered, the Kernel invokes the module bootstrap function.

Bootstrap is responsible for performing module initialization.

Typical bootstrap activities include:

- initializing internal state;
- allocating runtime resources;
- validating runtime conditions;
- preparing services for execution.

Bootstrap should not register additional resources.

Resource publication must already have been completed during the Resource Registration stage.

Once bootstrap completes successfully, the module is considered fully operational.

---

# Complete Module Tree

The following tree represents the complete reference implementation of an official Deja Platform module.

```text
module-name/
├── module.conf
├── module.sh
│
├── commands/
│   └── ...
│
├── services/
│   └── ...
│
├── capabilities/
│   └── ...
│
├── extensions/
│   ├── extension-point.sh
│   └── extension-provider.sh
│
├── providers/
│   └── ...
│
├── observers/
│   └── ...
│
├── config/
│   └── ...
│
├── docs/
│   └── ...
│
├── examples/
│   └── ...
│
└── tests/
    └── ...
```

This tree represents the complete architectural reference for modules developed using the Public Module SDK v1.

Individual modules are expected to contain only the directories required by their implementation.

---

# Complete Module Example

The following example illustrates the organization of a module that provides multiple platform resources.

```text
audit-module/
├── module.conf
├── module.sh
│
├── commands/
│   └── audit-report.sh
│
├── services/
│   └── audit-service.sh
│
├── capabilities/
│   └── audit-capability.sh
│
├── extensions/
│   ├── audit-extension-point.sh
│   └── audit-provider.sh
│
├── providers/
│   └── audit-config-provider.sh
│
├── observers/
│   └── audit-config-observer.sh
│
├── config/
│   └── audit.yaml
│
├── docs/
│   └── README.md
│
├── examples/
│   └── basic-usage.md
│
└── tests/
    └── audit-module-test.sh
```

This example demonstrates the official organization of a module.

Actual modules should include only the resources they implement.

---

# Module Author Checklist

Before publishing a module, authors should verify the following requirements.

## Structure

- [ ] `module.conf` is present.
- [ ] `module.sh` is present.
- [ ] Optional directories are used only when necessary.

## Manifest

- [ ] Module metadata is complete.
- [ ] Dependencies are correctly declared.
- [ ] Manifest follows the official specification.

## Resource Registration

- [ ] Resources are registered during the Resource Registration stage.
- [ ] Bootstrap does not register resources.
- [ ] Public APIs are used for every resource type.

## Bootstrap

- [ ] Bootstrap performs initialization only.
- [ ] Bootstrap is deterministic.
- [ ] Bootstrap does not modify module registration.

## Architecture

- [ ] Responsibilities are clearly separated.
- [ ] Public contracts are respected.
- [ ] No Kernel internals are accessed directly.
- [ ] Module follows the official directory structure.
- [ ] Naming conventions are respected.

Modules satisfying this checklist are considered compliant with the Public Module SDK v1.

---

# Public Module SDK v1 Compatibility

This document defines the official module architecture supported by the Public Module SDK v1.

Modules that comply with this specification are expected to remain compatible with future Kernel versions that preserve Public Module SDK v1 compatibility.

Kernel internals may evolve over time.

The Public Module SDK defines the compatibility boundary between the Kernel and platform modules.

For this reason, module authors should rely exclusively on documented public APIs and official architectural contracts.

---

# Revision History

| Version | Description |
|----------|-------------|
| Public Module SDK v1 | Initial official module architecture specification. |