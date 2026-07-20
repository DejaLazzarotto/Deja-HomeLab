# Module Command API

## Status

Official

## Since

Public Module SDK v1

## Purpose

The Module Command API allows modules to expose commands to the Deja Platform CLI.

Commands are one of the primary integration mechanisms between modules and the platform.

---

# Public API

## Register Command

```bash
platform_register_module_command \
    "<module>" \
    "<command>" \
    "<command_file>" \
    "<function>" \
    "<description>"
```

Registers a new command provided by a module.

### Parameters

| Parameter | Description |
|-----------|-------------|
| module | Module identifier |
| command | Command name exposed by the CLI |
| command_file | Script containing the implementation |
| function | Function executed by the command |
| description | Command description shown in help |

---

## Execute Command

```bash
platform_execute_module_command "<command>" [arguments...]
```

Executes a registered command.

Normally this function is invoked by the Platform CLI and does not need to be called directly by modules.

---

## Query APIs

### Check existence

```bash
platform_has_module_command "<command>"
```

Returns whether a command is registered.

---

### Get description

```bash
platform_get_module_command_description "<command>"
```

Returns the command description.

---

### Get origin

```bash
platform_get_module_command_origin "<command>"
```

Returns the module that registered the command.

---

### List commands

```bash
platform_list_module_commands
```

Returns all registered commands.

---

# Registration Lifecycle

Commands should be registered during the Resource Registration stage.

Example:

```bash
platform_module_example_register_resources() {
    platform_register_module_command \
        "example" \
        "example:hello" \
        "$PLATFORM_ROOT/modules/example/commands/hello.sh" \
        "platform_cmd_example_hello" \
        "Example command"
}
```

---

# Best Practices

- Register commands only once.
- Keep command implementations inside the module.
- Use namespaced command names.
- Avoid modifying commands registered by other modules.

---

# Compatibility

This API is part of the Public Module SDK v1.

Its behavior is covered by the SDK compatibility policy.