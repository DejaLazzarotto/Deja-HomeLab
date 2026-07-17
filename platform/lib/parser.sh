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

    if ! platform_command_exists "$command"; then
        platform_log_error "Unknown command: $command"
        echo
        platform_show_fallback_help
        return 1
    fi

    platform_command_dispatch "$command" "$@"
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

platform_show_fallback_help() {
    local command
    local description

    platform_log_info "Deja Platform CLI"

    echo
    echo "Usage:"
    echo "  platform <command>"
    echo
    echo "Available commands:"

    while IFS= read -r command; do
        [[ -z "$command" ]] && continue

        description="$(platform_get_command_description "$command")"
        printf "  %-12s %s\n" "$command" "$description"
    done < <(platform_list_commands)
}