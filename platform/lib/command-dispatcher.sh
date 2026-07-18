#!/usr/bin/env bash

#
# ==========================================================
# Deja Platform
# Command Dispatcher
# Internal Kernel Implementation
# ==========================================================
#

#
# Executa um comando registrado.
#
# Esta função nunca encerra diretamente o processo.
# Falhas são comunicadas exclusivamente pelo código de retorno.
#
platform_module_command_dispatch() {
    local command="${1:-}"
    local command_file
    local command_function

    if [[ -z "$command" ]]; then
        platform_log_error "Command name not informed for execution."
        return 1
    fi

    shift || true

    if ! platform_module_command_is_registered "$command"; then
        platform_log_error "Command not registered: $command"
        return 1
    fi

    command_file="$(platform_module_command_get_file "$command")"
    command_function="$(platform_module_command_get_function "$command")"

    if [[ -z "$command_file" ]]; then
        platform_log_error "Command file not registered: $command"
        return 1
    fi

    if [[ ! -f "$command_file" ]]; then
        platform_log_error "Command file not found: $command_file"
        return 1
    fi

    if [[ -z "$command_function" ]]; then
        platform_log_error "Command function not registered: $command"
        return 1
    fi

    source "$command_file" || {
        platform_log_error "Failed to load command implementation: $command"
        return 1
    }

    if ! declare -F "$command_function" >/dev/null; then
        platform_log_error "Invalid command implementation: $command"
        platform_log_error "Expected function: $command_function"
        return 1
    fi

    "$command_function" "$@"
}