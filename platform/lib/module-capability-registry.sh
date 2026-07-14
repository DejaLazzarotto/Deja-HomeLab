#!/usr/bin/env bash

#
# ==========================================================
# Deja Platform
# Module Capability Registry
# Internal Kernel Implementation
# ==========================================================
#

declare -gA PLATFORM_MODULE_CAPABILITY_MODULES=()
declare -ga PLATFORM_MODULE_CAPABILITY_NAMES=()

#
# Limpa completamente o registro de Capabilities.
#
platform_module_capability_registry_reset() {
    PLATFORM_MODULE_CAPABILITY_MODULES=()
    PLATFORM_MODULE_CAPABILITY_NAMES=()
}

#
# Registra uma Capability fornecida por um módulo.
#
platform_module_capability_register() {
    local module="${1:-}"
    local capability="${2:-}"
    local registered_module

    [[ -z "$module" ]] && return 1
    [[ -z "$capability" ]] && return 1

    registered_module="${PLATFORM_MODULE_CAPABILITY_MODULES[$capability]:-}"

    if [[ -n "$registered_module" ]]; then
        if [[ "$registered_module" == "$module" ]]; then
            return 0
        fi

        platform_log_error \
            "Capability already registered: capability=$capability module=$registered_module"

        return 1
    fi

    PLATFORM_MODULE_CAPABILITY_MODULES["$capability"]="$module"
    PLATFORM_MODULE_CAPABILITY_NAMES+=("$capability")
}

#
# Verifica se uma Capability está registrada.
#
platform_module_capability_exists() {
    local capability="${1:-}"

    [[ -z "$capability" ]] && return 1

    [[ -n "${PLATFORM_MODULE_CAPABILITY_MODULES[$capability]:-}" ]]
}

#
# Verifica se um módulo fornece determinada Capability.
#
platform_module_capability_module_has() {
    local module="${1:-}"
    local capability="${2:-}"

    [[ -z "$module" ]] && return 1
    [[ -z "$capability" ]] && return 1

    [[ "${PLATFORM_MODULE_CAPABILITY_MODULES[$capability]:-}" == "$module" ]]
}

#
# Retorna o módulo provedor de uma Capability.
#
platform_module_capability_get_module() {
    local capability="${1:-}"

    [[ -z "$capability" ]] && return 1

    platform_module_capability_exists "$capability" || return 1

    printf '%s\n' "${PLATFORM_MODULE_CAPABILITY_MODULES[$capability]}"
}

#
# Resolve uma Capability para seu módulo provedor.
#
platform_module_capability_resolve() {
    local capability="${1:-}"

    [[ -z "$capability" ]] && return 1

    if ! platform_module_capability_exists "$capability"; then
        platform_log_error "Capability not registered: $capability"
        return 1
    fi

    platform_module_capability_get_module "$capability"
}

#
# Lista todas as Capabilities registradas.
#
platform_module_capability_registry_list() {
    printf '%s\n' "${PLATFORM_MODULE_CAPABILITY_NAMES[@]}"
}

#
# Lista as Capabilities fornecidas por um módulo.
#
platform_module_capability_registry_list_by_module() {
    local module="${1:-}"
    local capability

    [[ -z "$module" ]] && return 1

    for capability in "${PLATFORM_MODULE_CAPABILITY_NAMES[@]}"; do
        if [[ "${PLATFORM_MODULE_CAPABILITY_MODULES[$capability]:-}" == "$module" ]]; then
            printf '%s\n' "$capability"
        fi
    done
}