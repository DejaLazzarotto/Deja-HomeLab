#!/usr/bin/env bash

platform_module_lifecycle_stage="discover"

platform_set_module_lifecycle_stage() {
  local stage="$1"

  case "$stage" in
    discover|load|bootstrap|ready)
      platform_module_lifecycle_stage="$stage"
      ;;
    *)
      platform_log_error "Invalid module lifecycle stage: $stage"
      return 1
      ;;
  esac
}

platform_get_module_lifecycle_stage() {
  echo "$platform_module_lifecycle_stage"
}

platform_bootstrap_modules() {
  platform_set_module_lifecycle_stage "bootstrap" || return 1
  platform_set_module_lifecycle_stage "ready" || return 1
}