# Module Command API Example

## Status

Official

---

# Purpose

This example demonstrates the minimal implementation required to publish a command using the Public Module SDK.

Only public SDK APIs are used.

---

# Prerequisites

Before implementing commands, a module must:

- Provide a valid module manifest.
- Implement the module entry point.
- Participate in the standard module lifecycle.

---

# Minimal SDK Usage

```bash
platform_register_module_command \
    "example" \
    "example:hello" \
    "$PLATFORM_ROOT/modules/example/commands/hello.sh" \
    "platform_cmd_example_hello" \
    "Print a greeting message"
```

The snippet above shows the minimum required interaction with the Public Module SDK.

---

# Complete Module Example

```bash
#!/usr/bin/env bash

platform_module_example_register_resources() {
    platform_register_module_command \
        "example" \
        "example:hello" \
        "$PLATFORM_ROOT/modules/example/commands/hello.sh" \
        "platform_cmd_example_hello" \
        "Print a greeting message"
}
```

```bash
#!/usr/bin/env bash

platform_cmd_example_hello() {
    platform_log_info "Hello from the example module."
}
```

---

# Explanation

The module registers a single command during the Resource Registration stage.

The command becomes available to the platform after the module bootstrap completes successfully.

The command implementation is completely independent from the registration process.

---

# Best Practices

- Register commands only during resource registration.
- Keep command implementations focused on a single responsibility.
- Use descriptive command names.
- Provide meaningful command descriptions.
- Keep registration separate from implementation.

---

# Common Mistakes

- Registering commands during bootstrap.
- Accessing internal Kernel functions.
- Mixing command registration with command implementation.
- Publishing commands without descriptions.

---

# Related APIs

- Module Lifecycle
- Module Development Guide
- Module Command API