#!/usr/bin/env bash

#
# ==========================================================
# Deja Platform
# Module State Registry
# Internal Kernel Implementation
# ==========================================================
#

declare -gA PLATFORM_MODULE_STATES=()

#
# Limpa completamente o registro de estados.
#
platform_module_state_reset() {
    PLATFORM_MODULE_STATES=()
}

#
# Define o estado atual de um módulo.
#
platform_module_state_set() {
    local module="${1:-}"
    local state="${2:-}"

    [[ -z "$module" ]] && return 1
    [[ -z "$state" ]] && return 1

    case "$state" in
        DISCOVERED|VALIDATED|RESOLVED|LOADED|BOOTSTRAPPED)
            ;;
        *)
            return 1
            ;;
    esac

    PLATFORM_MODULE_STATES["$module"]="$state"
}

#
# Retorna o estado atual do módulo.
#
platform_module_state_get() {
    local module="${1:-}"

    [[ -z "$module" ]] && return 1

    printf '%s\n' "${PLATFORM_MODULE_STATES[$module]}"
}

#
# Verifica se o módulo possui estado registrado.
#
platform_module_state_has() {
    local module="${1:-}"

    [[ -z "$module" ]] && return 1

    [[ -n "${PLATFORM_MODULE_STATES[$module]+x}" ]]
}

#
# Lista todos os módulos registrados.
#
platform_module_state_list() {
    printf '%s\n' "${!PLATFORM_MODULE_STATES[@]}"
}