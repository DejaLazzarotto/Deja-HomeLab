#!/usr/bin/env bash

platform_register_builtin_commands() {
  platform_register_command \
    "help" \
    "$PLATFORM_ROOT/commands/help.sh" \
    "platform_cmd_help" \
    "core" \
    "Show help"

  platform_register_command \
    "version" \
    "$PLATFORM_ROOT/commands/version.sh" \
    "platform_cmd_version" \
    "core" \
    "Show CLI version"

  platform_register_command \
    "doctor" \
    "$PLATFORM_ROOT/commands/doctor.sh" \
    "platform_cmd_doctor" \
    "core" \
    "Validate the platform environment"

  platform_register_command \
    "modules" \
    "$PLATFORM_ROOT/commands/modules.sh" \
    "platform_cmd_modules" \
    "core" \
    "List registered platform modules"
}