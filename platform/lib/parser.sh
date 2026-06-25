#!/usr/bin/env bash

platform_parse() {
  local command="${1:-help}"
  shift || true

  platform_dispatch_command "$command" "$@"
}

platform_dispatch_command() {
  local command="$1"
  shift || true

  local command_file="$PLATFORM_ROOT/commands/${command}.sh"
  local command_function="platform_cmd_${command}"

  case "$command" in
    --help|-h)
      command="help"
      command_file="$PLATFORM_ROOT/commands/help.sh"
      command_function="platform_cmd_help"
      ;;

    --version|-v)
      command="version"
      command_file="$PLATFORM_ROOT/commands/version.sh"
      command_function="platform_cmd_version"
      ;;
  esac

  if [[ ! -f "$command_file" ]]; then
    platform_log_error "Unknown command: $command"
    echo ""
    platform_show_fallback_help
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
  echo "  version    Show CLI version"
  echo "  help       Show help"
  echo "  doctor     Validate the platform environment"
}