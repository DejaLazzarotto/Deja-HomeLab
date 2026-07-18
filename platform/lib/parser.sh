#!/usr/bin/env bash

#
# ==========================================================
# Deja Platform
# CLI Command Parser
# ==========================================================
#

platform_parse() {
    local command="${1:-help}"

    shift || true

    command="$(platform_normalize_command "$command")"

    if ! platform_module_command_is_registered "$command"; then
        platform_log_error "Unknown command: $command"
        echo
        platform_module_command_dispatch "help"
        return 1
    fi

    platform_module_command_dispatch "$command" "$@"
}

platform_normalize_command() {
    local command="${1:-help}"

    case "$command" in
        --help|-h)
            printf '%s\n' "help"
            ;;
        --version|-v)
            printf '%s\n' "version"
            ;;
        *)
            printf '%s\n' "$command"
            ;;
    esac
}