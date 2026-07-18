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

    platform_module_command_register \
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

    platform_module_command_is_registered "$command"
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

    if ! platform_module_command_is_registered "$command"; then
        platform_log_error "Command not registered: $command"
        return 1
    fi

    platform_module_command_get_origin "$command"
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

    if ! platform_module_command_is_registered "$command"; then
        platform_log_error "Command not registered: $command"
        return 1
    fi

    platform_module_command_get_description "$command"
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

        command_origin="$(platform_module_command_get_origin "$command")"

        if [[ "$command_origin" == "$module" ]]; then
            printf '%s\n' "$command"
        fi
    done < <(platform_module_command_registry_list)
}

#
# Executa um comando registrado.
#
# A API pública apenas delega a execução ao Dispatcher interno.
# Falhas são comunicadas exclusivamente pelo código de retorno.
#
platform_execute_module_command() {
    local command="${1:-}"

    if [[ -z "$command" ]]; then
        platform_log_error "Command name not informed for execution."
        return 1
    fi

    shift || true

    platform_module_command_dispatch "$command" "$@"
}