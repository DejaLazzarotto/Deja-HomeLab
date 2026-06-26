#!/usr/bin/env bash

platform_register_module_command() {
  local module_name="$1"
  local command_name="$2"
  local command_file="$3"
  local command_function="$4"
  local command_description="${5:-}"

  if [[ -z "$module_name" || -z "$command_name" || -z "$command_file" || -z "$command_function" ]]; then
    platform_log_error "Invalid module command registration"
    return 1
  fi

  platform_register_command \
    "$command_name" \
    "$command_file" \
    "$command_function" \
    "$module_name" \
    "$command_description"
}