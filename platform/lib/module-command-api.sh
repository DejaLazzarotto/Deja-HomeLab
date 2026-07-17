#!/usr/bin/env bash

#
# ==========================================================
# Deja Platform
# Module Command Public API
# ==========================================================
#

#
# Registra um comando pertencente a um módulo.
#
# Parâmetros:
#   $1 - Nome do módulo
#   $2 - Nome público do comando
#   $3 - Arquivo que implementa o comando
#   $4 - Nome da função de implementação
#   $5 - Descrição opcional
#
platform_register_module_command() {
    local module="${1:-}"
    local command="${2:-}"
    local command_file="${3:-}"
    local command_function="${4:-}"
    local description="${5:-}"

    if [[ -z "$module" ]]; then
        platform_log_error "Module name not informed for command registration."
        return 1
    fi

    if [[ -z "$command" ]]; then
        platform_log_error "Command name not informed."
        return 1
    fi

    if [[ -z "$command_file" ]]; then
        platform_log_error "Command file not informed: $command"
        return 1
    fi

    if [[ -z "$command_function" ]]; then
        platform_log_error "Command function not informed: $command"
        return 1
    fi

    platform_register_command \
        "$command" \
        "$command_file" \
        "$command_function" \
        "$module" \
        "$description"
}

#
# Verifica se um comando está registrado.
#
platform_has_module_command() {
    local command="${1:-}"

    if [[ -z "$command" ]]; then
        return 1
    fi

    platform_command_exists "$command"
}

#
# Retorna o módulo que registrou o comando.
#
platform_get_module_command_origin() {
    local command="${1:-}"

    if [[ -z "$command" ]]; then
        platform_log_error "Command name not informed."
        return 1
    fi

    if ! platform_command_exists "$command"; then
        platform_log_error "Command not registered: $command"
        return 1
    fi

    platform_get_command_origin "$command"
}

#
# Retorna a descrição pública do comando.
#
platform_get_module_command_description() {
    local command="${1:-}"

    if [[ -z "$command" ]]; then
        platform_log_error "Command name not informed."
        return 1
    fi

    if ! platform_command_exists "$command"; then
        platform_log_error "Command not registered: $command"
        return 1
    fi

    platform_get_command_description "$command"
}

#
# Lista os comandos registrados.
#
# Quando um módulo for informado, somente os comandos pertencentes
# a esse módulo serão retornados.
#
platform_list_module_commands() {
    local module="${1:-}"
    local command
    local command_origin

    while IFS= read -r command; do
        [[ -z "$command" ]] && continue

        if [[ -z "$module" ]]; then
            printf '%s\n' "$command"
            continue
        fi

        command_origin="$(platform_get_command_origin "$command")"

        if [[ "$command_origin" == "$module" ]]; then
            printf '%s\n' "$command"
        fi
    done < <(platform_list_commands)
}

#
# Executa um comando registrado.
#
# Diferentemente do dispatcher da CLI, esta função nunca encerra
# diretamente o processo. Falhas são comunicadas pelo código de retorno.
#
platform_execute_module_command() {
    local command="${1:-}"
    local command_file
    local command_function

    if [[ -z "$command" ]]; then
        platform_log_error "Command name not informed for execution."
        return 1
    fi

    shift || true

    if ! platform_command_exists "$command"; then
        platform_log_error "Command not registered: $command"
        return 1
    fi

    command_file="$(platform_get_command_file "$command")"
    command_function="$(platform_get_command_function "$command")"

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