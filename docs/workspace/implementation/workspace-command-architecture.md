# Workspace SDK — Command Architecture

## Overview

The Workspace Command Architecture establishes the official infrastructure for executable actions inside the Deja Workspace.

Commands provide a unified execution model shared by every user interaction mechanism.

This architecture becomes the single execution layer used by:

- Toolbar
- Main Menu
- Context Menu
- Command Palette
- Keyboard Shortcuts
- Actions
- Runtime APIs
- Workspace Modules

---

# Objectives

The Command infrastructure is responsible for:

- registering executable commands;
- locating commands by identifier;
- validating execution;
- executing synchronous and asynchronous handlers;
- standardizing execution results;
- exposing commands to the Workspace Runtime.

---

# Architecture

Workspace Commands are composed of three primary components.

## WorkspaceCommand

Defines the official contract of an executable command.

Responsibilities include:

- metadata;
- ownership;
- execution handler;
- execution policy;
- UI information;
- search metadata.

---

## WorkspaceCommandRegistry

Responsible for:

- registration;
- duplicate prevention;
- lookup;
- removal;
- owner queries;
- immutable snapshots.

---

## WorkspaceCommandDispatcher

Responsible for:

- execution;
- context creation;
- canExecute validation;
- result normalization;
- execution error handling.

---

## Runtime Integration

The WorkspaceRuntime owns:

- one WorkspaceCommandRegistry;
- one WorkspaceCommandDispatcher.

Modules register commands directly through the Runtime.

UI components never execute commands directly.

Instead, they always invoke the Runtime dispatcher.

This guarantees a single execution pipeline across the entire Workspace.

---

# Execution Flow

Module

↓

WorkspaceRuntime

↓

WorkspaceCommandRegistry

↓

WorkspaceCommandDispatcher

↓

WorkspaceCommand

↓

Result

---

# Current Status

Implemented:

- WorkspaceCommand
- WorkspaceCommandRegistry
- WorkspaceCommandDispatcher
- Runtime integration

Future integrations:

- Toolbar
- Menu
- Context Menu
- Command Palette
- Keyboard Shortcuts
- Actions
- Search Providers

---

End of W3.5