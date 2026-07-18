#!/usr/bin/env bash

#
# ==========================================================
# Deja Platform
# Module Command Registry
# Internal Kernel Implementation
# ==========================================================
#

declare -ga PLATFORM_MODULE_COMMAND_NAMES=()
declare -gA PLATFORM_MODULE_COMMAND_FILES=()
declare -gA PLATFORM_MODULE_COMMAND_FUNCTIONS=()
declare -gA PLATFORM_MODULE_COMMAND_ORIGINS=()
declare -gA PLATFORM_MODULE_COMMAND_DESCRIPTIONS=()

#
# Limpa completamente o registro de Commands.
#
platform_module_command_registry_reset() {
    PLATFORM_MODULE_COMMAND_NAMES=()
    PLATFORM_MODULE_COMMAND_FILES=()
    PLATFORM_MODULE_COMMAND_FUNCTIONS=()
    PLATFORM_MODULE_COMMAND_ORIGINS=()
    PLATFORM_MODULE_COMMAND_DESCRIPTIONS=()
}

#
# Registra um Command interno.
#
platform_module_command_register() {
    local command="${1:-}"
    local command_file="${2:-}"
    local command_function="${3:-}"
    local origin="${4:-core}"
    local description="${5:-}"

    if [[ -z "$command" || -z "$command_file" || -z "$command_function" ]]; then
        platform_log_error "Invalid command registration"
        return 1
    fi

    if platform_module_command_is_registered "$command"; then
        platform_log_error "Command already registered: $command"
        return 1
    fi

    PLATFORM_MODULE_COMMAND_NAMES+=("$command")
    PLATFORM_MODULE_COMMAND_FILES["$command"]="$command_file"
    PLATFORM_MODULE_COMMAND_FUNCTIONS["$command"]="$command_function"
    PLATFORM_MODULE_COMMAND_ORIGINS["$command"]="$origin"
    PLATFORM_MODULE_COMMAND_DESCRIPTIONS["$command"]="$description"

    return 0
}

#
# Verifica se um Command está registrado.
#
platform_module_command_is_registered() {
    local command="${1:-}"

    [[ -z "$command" ]] && return 1

    [[ -n "${PLATFORM_MODULE_COMMAND_FILES[$command]+x}" ]]
}

#
# Retorna o arquivo que implementa o Command.
#
platform_module_command_get_file() {
    local command="${1:-}"

    [[ -z "$command" ]] && return 1

    printf '%s\n' "${PLATFORM_MODULE_COMMAND_FILES[$command]:-}"
}

#
# Retorna a função que implementa o Command.
#
platform_module_command_get_function() {
    local command="${1:-}"

    [[ -z "$command" ]] && return 1

    printf '%s\n' "${PLATFORM_MODULE_COMMAND_FUNCTIONS[$command]:-}"
}

#
# Retorna a origem proprietária do Command.
#
platform_module_command_get_origin() {
    local command="${1:-}"

    [[ -z "$command" ]] && return 1

    printf '%s\n' "${PLATFORM_MODULE_COMMAND_ORIGINS[$command]:-}"
}

#
# Retorna a descrição pública do Command.
#
platform_module_command_get_description() {
    local command="${1:-}"

    [[ -z "$command" ]] && return 1

    printf '%s\n' "${PLATFORM_MODULE_COMMAND_DESCRIPTIONS[$command]:-}"
}

#
# Lista todos os Commands registrados na ordem de registro.
#
platform_module_command_registry_list() {
    printf '%s\n' "${PLATFORM_MODULE_COMMAND_NAMES[@]}"
}