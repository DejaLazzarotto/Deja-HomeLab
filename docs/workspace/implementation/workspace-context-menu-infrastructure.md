# Workspace Context Menu Infrastructure

## Phase

W3.7.3

---

## Objective

Establish the official infrastructure responsible for the Workspace Context Menus.

The Context Menu infrastructure belongs to the Workspace UI Infrastructure layer and is completely independent from Angular or any rendering engine.

Its responsibility is to define the available contextual actions presented by the user interface while delegating all execution to the Workspace Action Architecture.

---

# Architecture

```text
Workspace Context Menu
        │
        ▼
Workspace Action
        │
        ▼
Workspace Command
        │
        ▼
Business Logic
```

Context Menus never execute business logic directly.

Every executable item references exclusively a WorkspaceAction.

---

# Components

This phase introduces the following components.

## WorkspaceContextMenu

Public contract describing a Context Menu.

Responsibilities:

- define menu identity;
- define ordering;
- define entries.

---

## WorkspaceContextMenuItem

Represents an executable Context Menu entry.

Each item references exactly one:

- WorkspaceActionId

Never:

- WorkspaceCommandId

---

## WorkspaceContextMenuGroup

Logical grouping of Context Menu entries.

---

## WorkspaceContextMenuSeparator

Visual separator between menu entries.

---

## WorkspaceContextMenuRegistry

Official registry responsible for:

- registration;
- lookup;
- removal;
- ordering.

---

# Runtime Integration

WorkspaceRuntime now provides the official Context Menu API.

Available operations:

- registerContextMenu()
- registerContextMenus()
- unregisterContextMenu()
- contextMenus()
- getContextMenu()
- hasContextMenu()

The Runtime also clears the registry during reset(), preserving lifecycle consistency.

---

# UI Infrastructure

The official UI Infrastructure is now composed of:

- Workspace Menus
- Workspace Toolbars
- Workspace Context Menus

Each infrastructure is completely independent while sharing the Workspace Action Architecture.

---

# Architectural Principles

The Context Menu infrastructure must always remain:

- Angular independent;
- renderer independent;
- Action based;
- Runtime integrated;
- deterministic;
- strongly typed.

---

# Result

The Workspace SDK now provides an official Context Menu infrastructure fully integrated with the Runtime while preserving complete separation between UI interaction and business logic.

This concludes Phase W3.7.3.