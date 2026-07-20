# Module Command API

## Status

Official

## Since

Public Module SDK v1

---

# Purpose

The Module Command API allows modules to register, inspect and execute commands exposed through the Deja Platform command system.

Commands are one of the primary integration mechanisms between modules and the platform CLI.

The public API delegates command storage and execution to internal Kernel components without exposing their implementation details.

---

# Public Functions

## `platform_register_module_command()`

Registers a command provided by a module.

```bash
platform_register_module_command \
    "<module>" \
    "<command>" \
    "<command_file>" \
    "<command_function>" \
    ["<description>"]
```

### Parameters

| Parameter          | Required | Description                                     |
| ------------------ | -------- | ----------------------------------------------- |
| `module`           | Yes      | Identifier of the module providing the command. |
| `command`          | Yes      | Public command name exposed by the platform.    |
| `command_file`     | Yes      | File containing the command implementation.     |
| `command_function` | Yes      | Function invoked when the command is executed.  |
| `description`      | No       | Public description of the command.              |

Example:

```bash
platform_register_module_command \
    "example" \
    "example:hello" \
    "$PLATFORM_ROOT/modules/example/commands/hello.sh" \
    "platform_cmd_example_hello" \
    "Print an example greeting"
```

Command registration fails when required parameters are missing or when the internal Command Registry rejects the registration.

---

## `platform_has_module_command()`

Checks whether a command is registered.

```bash
platform_has_module_command "<command>"
```

Return status:

| Status | Meaning                                                        |
| ------ | -------------------------------------------------------------- |
| `0`    | The command is registered.                                     |
| `1`    | The command is not registered or no command name was provided. |

Example:

```bash
if platform_has_module_command "example:hello"; then
    echo "Command is registered."
fi
```

---

## `platform_get_module_command_origin()`

Returns the module that registered a command.

```bash
platform_get_module_command_origin "<command>"
```

Example:

```bash
command_origin="$(
    platform_get_module_command_origin "example:hello"
)" || return 1
```

The operation fails when the command name is missing or the command is not registered.

---

## `platform_get_module_command_description()`

Returns the public description of a registered command.

```bash
platform_get_module_command_description "<command>"
```

Example:

```bash
command_description="$(
    platform_get_module_command_description "example:hello"
)" || return 1
```

The operation fails when the command name is missing or the command is not registered.

---

## `platform_list_module_commands()`

Lists registered commands.

```bash
platform_list_module_commands ["<module>"]
```

When no module is provided, all registered commands are returned.

```bash
platform_list_module_commands
```

When a module is provided, only commands registered by that module are returned.

```bash
platform_list_module_commands "example"
```

Each command name is printed on a separate line.

---

## `platform_execute_module_command()`

Executes a registered command.

```bash
platform_execute_module_command "<command>" [arguments...]
```

Example:

```bash
platform_execute_module_command \
    "example:hello" \
    "Deja Platform"
```

The command name is removed from the argument list before the remaining arguments are forwarded to the command implementation.

The public API delegates execution to the internal Command Dispatcher.

Execution success or failure is communicated through the command return status.

This function is normally invoked by the platform CLI. Modules should call it directly only when command-to-command delegation is intentional.

---

# Registration Lifecycle

Commands should be registered during the Resource Registration stage.

```bash
platform_module_example_register_resources() {
    platform_register_module_command \
        "example" \
        "example:hello" \
        "$PLATFORM_ROOT/modules/example/commands/hello.sh" \
        "platform_cmd_example_hello" \
        "Print an example greeting"
}
```

Command implementations should be defined separately from the module entrypoint.

Example implementation:

```bash
platform_cmd_example_hello() {
    local name="${1:-World}"

    printf 'Hello, %s!\n' "$name"
}
```

---

# Command Naming

Module commands should use a namespace based on the module identifier.

Recommended format:

```text
<module>:<command>
```

Examples:

```text
example:hello
backup:create
network:status
```

Namespaced commands reduce collisions between modules and make command ownership explicit.

---

# Usage Rules

Modules must not access:

* the internal Command Registry;
* the internal Command Dispatcher;
* command registry storage variables;
* commands owned by another module through internal functions.

The Public Module SDK v1 does not expose an operation for unregistering commands.

Commands are expected to remain registered for the active platform runtime after successful resource registration.

---

# Best Practices

* Register commands only during Resource Registration.
* Register each command only once.
* Use namespaced command names.
* Keep implementations inside the module directory.
* Keep command functions small and focused.
* Validate command arguments inside the implementation.
* Return nonzero status codes when execution fails.
* Do not replace or modify commands registered by other modules.

---

# Compatibility

The following functions are part of the Public Module SDK v1 compatibility contract:

```text
platform_register_module_command
platform_has_module_command
platform_get_module_command_origin
platform_get_module_command_description
platform_list_module_commands
platform_execute_module_command
```

Internal Command Registry and Command Dispatcher functions are not part of the public compatibility contract.
