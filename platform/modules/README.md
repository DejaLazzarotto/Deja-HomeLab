# Deja Platform Modules

This directory contains internal platform modules.

Modules are extension points for the Deja Platform CLI and must not replace the core command dispatcher.

## Purpose

The modules layer exists to prepare the platform for modular command registration and future internal extensions.

## Rules

- Core CLI bootstrap remains in `platform/bin/platform`.
- Core command dispatch remains in `platform/lib/parser.sh`.
- Built-in commands remain in `platform/commands`.
- Reusable shell libraries remain in `platform/lib`.
- Modules must be loaded by the platform core, not executed directly.