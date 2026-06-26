#!/usr/bin/env bash

platform_cmd_help() {
  platform_log_info "Deja Platform CLI"
  echo ""
  echo "Usage:"
  echo "  platform <command>"
  echo ""
  echo "Available commands:"
  echo "  version    Show CLI version"
  echo "  help       Show help"
  echo "  doctor     Validate the platform environment"
  echo "  modules    List registered platform modules"
}