#!/usr/bin/env bash

PLATFORM_MODULES=()

platform_register_module() {
  local module_name="${1:-}"

  if [[ -z "$module_name" ]]; then
    platform_log_error "Module name is required"
    return 1
  fi

  PLATFORM_MODULES+=("$module_name")
}

platform_list_modules() {
  local module

  for module in "${PLATFORM_MODULES[@]}"; do
    echo "$module"
  done
}