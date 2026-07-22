# ADR-002 — Workspace Command Architecture

## Status

Accepted

---

## Context

The Workspace Runtime requires a unified mechanism for exposing executable actions independently of the user interface.

Prior to this ADR, execution logic could potentially become distributed across multiple UI components such as menus, toolbars or context menus.

A single execution pipeline is required to guarantee consistency, extensibility and modularity.

---

## Decision

The Workspace SDK adopts the Workspace Command Architecture composed of three official components:

- WorkspaceCommand
- WorkspaceCommandRegistry
- WorkspaceCommandDispatcher

The WorkspaceRuntime becomes the single owner of the command infrastructure.

Modules register commands through the Runtime.

All UI layers invoke commands exclusively through the Runtime dispatcher.

---

## Consequences

### Positive

- single execution pipeline;
- UI-independent commands;
- modular registration;
- centralized validation;
- centralized execution;
- simplified testing;
- reusable by future UI components;
- foundation for Command Palette;
- foundation for keyboard shortcuts;
- foundation for automation and scripting.

### Negative

- introduces an additional abstraction layer;
- requires all execution paths to use the Runtime dispatcher.

---

## Alternatives Considered

### UI-owned commands

Rejected.

This approach would tightly couple execution logic with visual components.

---

### Module-local execution

Rejected.

Execution would become fragmented and difficult to audit.

---

## Architecture Impact

No changes to:

- Workspace Registry Architecture;
- Runtime Extension Architecture;
- Workspace SDK public contracts.

This ADR introduces only the official command execution infrastructure.

---

## References

- W3.5 — Workspace Command Architecture
- ADR-001 — Runtime Registry Architecture