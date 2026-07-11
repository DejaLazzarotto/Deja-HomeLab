#!/usr/bin/env bash

platform_reset_module_manifest() {
  unset \
    MODULE_NAME \
    MODULE_VERSION \
    MODULE_DESCRIPTION \
    MODULE_AUTHOR \
    MODULE_API_VERSION \
    MODULE_ENTRYPOINT \
    MODULE_DEPENDENCIES \
    MODULE_ENABLED
}

platform_validate_module_manifest() {
  local manifest_file="$1"

  platform_require_variable "MODULE_NAME" || {
    platform_log_error "Invalid module manifest: $manifest_file"
    return 1
  }

  platform_require_variable "MODULE_VERSION" || {
    platform_log_error "Invalid module manifest: $manifest_file"
    return 1
  }

  platform_require_variable "MODULE_API_VERSION" || {
    platform_log_error "Invalid module manifest: $manifest_file"
    return 1
  }

  platform_require_variable "MODULE_ENTRYPOINT" || {
    platform_log_error "Invalid module manifest: $manifest_file"
    return 1
  }

  platform_require_variable "MODULE_ENABLED" || {
    platform_log_error "Invalid module manifest: $manifest_file"
    return 1
  }

  case "$MODULE_ENABLED" in
    true|false)
      ;;
    *)
      platform_log_error "Invalid MODULE_ENABLED value in: $manifest_file"
      return 1
      ;;
  esac

  return 0
}

platform_read_module_manifest() {
  local manifest_file="${1:-}"

  if [[ -z "$manifest_file" ]]; then
    platform_log_error "Module manifest path is required"
    return 1
  fi

  platform_require_readable_file "$manifest_file" || return 1

  platform_reset_module_manifest

  source "$manifest_file"

  platform_validate_module_manifest "$manifest_file"
}