#!/usr/bin/env bash

PLATFORM_COMMAND_NAMES=()
PLATFORM_COMMAND_FILES=()
PLATFORM_COMMAND_FUNCTIONS=()
PLATFORM_COMMAND_ORIGINS=()
PLATFORM_COMMAND_DESCRIPTIONS=()

platform_register_command() {
  local command_name="${1:-}"
  local command_file="${2:-}"
  local command_function="${3:-}"
  local command_origin="${4:-core}"
  local command_description="${5:-}"

  [[ -n "$command_name" ]] || return 1
  [[ -n "$command_file" ]] || return 1
  [[ -n "$command_function" ]] || return 1

  PLATFORM_COMMAND_NAMES+=("$command_name")
  PLATFORM_COMMAND_FILES+=("$command_file")
  PLATFORM_COMMAND_FUNCTIONS+=("$command_function")
  PLATFORM_COMMAND_ORIGINS+=("$command_origin")
  PLATFORM_COMMAND_DESCRIPTIONS+=("$command_description")
}

platform_command_index() {
  local expected="${1:-}"
  local index

  [[ -n "$expected" ]] || return 1

  for index in "${!PLATFORM_COMMAND_NAMES[@]}"; do
    if [[ "${PLATFORM_COMMAND_NAMES[$index]}" == "$expected" ]]; then
      echo "$index"
      return 0
    fi
  done

  return 1
}

platform_command_exists() {
  local command_name="${1:-}"

  platform_command_index "$command_name" >/dev/null
}

platform_command_file() {
  local command_name="${1:-}"
  local index

  index="$(platform_command_index "$command_name")" || return 1

  echo "${PLATFORM_COMMAND_FILES[$index]}"
}

platform_command_function() {
  local command_name="${1:-}"
  local index

  index="$(platform_command_index "$command_name")" || return 1

  echo "${PLATFORM_COMMAND_FUNCTIONS[$index]}"
}

platform_command_origin() {
  local command_name="${1:-}"
  local index

  index="$(platform_command_index "$command_name")" || return 1

  echo "${PLATFORM_COMMAND_ORIGINS[$index]}"
}

platform_command_description() {
  local command_name="${1:-}"
  local index

  index="$(platform_command_index "$command_name")" || return 1

  echo "${PLATFORM_COMMAND_DESCRIPTIONS[$index]}"
}

platform_list_commands() {
  local index

  for index in "${!PLATFORM_COMMAND_NAMES[@]}"; do
    echo "${PLATFORM_COMMAND_NAMES[$index]}"
  done
}