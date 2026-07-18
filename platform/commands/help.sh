#!/usr/bin/env bash

platform_cmd_help() {
  platform_log_info "Deja Platform CLI"
  echo ""
  echo "Usage:"
  echo "  platform <command>"
  echo ""
  echo "Available commands:"

  local command
  local description

  for command in $(platform_list_module_commands); do
    description="$(platform_get_module_command_description "$command")"
    printf "  %-12s %s\n" "$command" "$description"
  done
}