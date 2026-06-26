#!/usr/bin/env bash

PLATFORM_COMMAND_NAMES=()
declare -A PLATFORM_COMMAND_FILES
declare -A PLATFORM_COMMAND_FUNCTIONS
declare -A PLATFORM_COMMAND_ORIGINS
declare -A PLATFORM_COMMAND_DESCRIPTIONS

platform_register_command() {
  local name="$1"
  local file="$2"
  local function_name="$3"
  local origin="${4:-core}"
  local description="${5:-}"

  if [[ -z "$name" || -z "$file" || -z "$function_name" ]]; then
    platform_log_error "Invalid command registration"
    return 1
  fi

  if platform_command_exists "$name"; then
    platform_log_error "Command already registered: $name"
    return 1
  fi

  PLATFORM_COMMAND_NAMES+=("$name")
  PLATFORM_COMMAND_FILES["$name"]="$file"
  PLATFORM_COMMAND_FUNCTIONS["$name"]="$function_name"
  PLATFORM_COMMAND_ORIGINS["$name"]="$origin"
  PLATFORM_COMMAND_DESCRIPTIONS["$name"]="$description"
}

platform_command_exists() {
  local name="$1"

  [[ -n "${PLATFORM_COMMAND_FILES[$name]:-}" ]]
}

platform_get_command_file() {
  local name="$1"

  echo "${PLATFORM_COMMAND_FILES[$name]:-}"
}

platform_get_command_function() {
  local name="$1"

  echo "${PLATFORM_COMMAND_FUNCTIONS[$name]:-}"
}

platform_get_command_origin() {
  local name="$1"

  echo "${PLATFORM_COMMAND_ORIGINS[$name]:-}"
}

platform_get_command_description() {
  local name="$1"

  echo "${PLATFORM_COMMAND_DESCRIPTIONS[$name]:-}"
}

platform_list_commands() {
  local name

  for name in "${PLATFORM_COMMAND_NAMES[@]}"; do
    echo "$name"
  done
}