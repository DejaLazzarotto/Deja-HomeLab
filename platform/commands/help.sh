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

  for command in $(platform_module_command_registry_list); do
    description="$(platform_module_command_get_description "$command")"
    printf "  %-12s %s\n" "$command" "$description"
  done
}