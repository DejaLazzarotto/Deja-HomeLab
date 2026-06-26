#!/usr/bin/env bash

platform_register_module "core"

platform_register_module_command \
  "core" \
  "core:status" \
  "$PLATFORM_ROOT/modules/core/status.sh" \
  "platform_cmd_core_status" \
  "Show core module status"