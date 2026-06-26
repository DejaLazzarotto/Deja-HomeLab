#!/usr/bin/env bash

platform_parse() {
  local command="${1:-help}"
  shift || true

  command="$(platform_normalize_command "$command")"

  platform_dispatch_command "$command" "$@"
}

platform_normalize_command() {
  local command="${1:-help}"

  case "$command" in
    --help|-h)
      echo "help"
      ;;
    --version|-v)
      echo "version"
      ;;
    *)
      echo "$command"
      ;;
  esac
}

platform_dispatch_command() {
  local command="$1"
  shift || true

  local command_file
  local command_function

  if ! platform_command_exists "$command"; then
    platform_log_error "Unknown command: $command"
    echo ""
    platform_show_fallback_help
    exit 1
  fi

  command_file="$(platform_get_command_file "$command")"
  command_function="$(platform_get_command_function "$command")"

  if [[ ! -f "$command_file" ]]; then
    platform_log_error "Command file not found: $command_file"
    exit 1
  fi

  source "$command_file"

  if ! declare -F "$command_function" >/dev/null; then
    platform_log_error "Invalid command implementation: $command"
    platform_log_error "Expected function: $command_function"
    exit 1
  fi

  "$command_function" "$@"
}

platform_show_fallback_help() {
  platform_log_info "Deja Platform CLI"
  echo ""
  echo "Usage:"
  echo "  platform <command>"
  echo ""
  echo "Available commands:"

  local command
  local description

  for command in $(platform_list_commands); do
    description="$(platform_get_command_description "$command")"
    printf "  %-12s %s\n" "$command" "$description"
  done
}