#!/usr/bin/env bash

# Shared validation helpers for Deja Platform CLI.

platform_require_command() {
  local command_name="$1"

  if ! command -v "$command_name" >/dev/null 2>&1; then
    platform_log_error "Required command not found: $command_name"
    return 1
  fi

  return 0
}

platform_require_directory() {
  local directory_path="$1"

  if [[ ! -d "$directory_path" ]]; then
    platform_log_error "Required directory not found: $directory_path"
    return 1
  fi

  return 0
}

platform_require_file() {
  local file_path="$1"

  if [[ ! -f "$file_path" ]]; then
    platform_log_error "Required file not found: $file_path"
    return 1
  fi

  return 0
}

platform_require_readable_file() {
  local file_path="$1"

  platform_require_file "$file_path" || return 1

  if [[ ! -r "$file_path" ]]; then
    platform_log_error "File is not readable: $file_path"
    return 1
  fi

  return 0
}

platform_require_executable_file() {
  local file_path="$1"

  platform_require_file "$file_path" || return 1

  if [[ ! -x "$file_path" ]]; then
    platform_log_error "File is not executable: $file_path"
    return 1
  fi

  return 0
}

platform_require_variable() {
  local variable_name="$1"
  local variable_value="${!variable_name:-}"

  if [[ -z "$variable_value" ]]; then
    platform_log_error "Required variable is not set: $variable_name"
    return 1
  fi

  return 0
}