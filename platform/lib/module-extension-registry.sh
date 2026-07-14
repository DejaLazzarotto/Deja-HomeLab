#!/usr/bin/env bash

#
# ==========================================================
# Deja Platform
# Module Extension Point Registry
# Internal Kernel Implementation
# ==========================================================
#

declare -gA PLATFORM_MODULE_EXTENSION_POINTS=()
declare -gA PLATFORM_MODULE_EXTENSION_PROVIDERS=()
declare -gA PLATFORM_MODULE_EXTENSION_PROVIDER_FUNCTIONS=()

#
# Limpa completamente o registro de Extension Points
# e seus Providers.
#
platform_module_extension_registry_reset() {
    PLATFORM_MODULE_EXTENSION_POINTS=()
    PLATFORM_MODULE_EXTENSION_PROVIDERS=()
    PLATFORM_MODULE_EXTENSION_PROVIDER_FUNCTIONS=()
}

#
# Registra um Extension Point interno do Kernel.
#
platform_module_extension_register() {
    local extension_point="${1:-}"

    if [[ -z "$extension_point" ]]; then
        platform_log_error "Extension point name not informed."
        return 1
    fi

    if [[ -n "${PLATFORM_MODULE_EXTENSION_POINTS[$extension_point]+x}" ]]; then
        platform_log_error "Extension point already registered: $extension_point"
        return 1
    fi

    PLATFORM_MODULE_EXTENSION_POINTS["$extension_point"]="registered"
}

#
# Verifica se um Extension Point está registrado.
#
platform_module_extension_is_registered() {
    local extension_point="${1:-}"

    [[ -z "$extension_point" ]] && return 1

    [[ -n "${PLATFORM_MODULE_EXTENSION_POINTS[$extension_point]+x}" ]]
}

#
# Registra um Provider para um Extension Point.
#
# Nesta fase, cada Extension Point aceita apenas um Provider.
#
platform_module_extension_register_provider() {
    local extension_point="${1:-}"
    local provider_module="${2:-}"
    local provider_function="${3:-}"

    if [[ -z "$extension_point" ]]; then
        platform_log_error "Extension point name not informed."
        return 1
    fi

    if [[ -z "$provider_module" ]]; then
        platform_log_error "Extension provider module not informed."
        return 1
    fi

    if [[ -z "$provider_function" ]]; then
        platform_log_error "Extension provider function not informed."
        return 1
    fi

    if ! platform_module_extension_is_registered "$extension_point"; then
        platform_log_error "Unknown extension point: $extension_point"
        return 1
    fi

    if [[ -n "${PLATFORM_MODULE_EXTENSION_PROVIDERS[$extension_point]+x}" ]]; then
        platform_log_error "Extension provider already registered: $extension_point"
        return 1
    fi

    if ! declare -F "$provider_function" >/dev/null 2>&1; then
        platform_log_error "Extension provider function not found: $provider_function"
        return 1
    fi

    PLATFORM_MODULE_EXTENSION_PROVIDERS["$extension_point"]="$provider_module"
    PLATFORM_MODULE_EXTENSION_PROVIDER_FUNCTIONS["$extension_point"]="$provider_function"
}

#
# Retorna o módulo Provider registrado para um Extension Point.
#
platform_module_extension_get_provider() {
    local extension_point="${1:-}"

    if [[ -z "$extension_point" ]]; then
        platform_log_error "Extension point name not informed."
        return 1
    fi

    if ! platform_module_extension_is_registered "$extension_point"; then
        platform_log_error "Unknown extension point: $extension_point"
        return 1
    fi

    if [[ -z "${PLATFORM_MODULE_EXTENSION_PROVIDERS[$extension_point]+x}" ]]; then
        platform_log_error "No provider registered for extension point: $extension_point"
        return 1
    fi

    printf '%s\n' "${PLATFORM_MODULE_EXTENSION_PROVIDERS[$extension_point]}"
}

#
# Retorna a função Provider registrada para um Extension Point.
#
platform_module_extension_get_provider_function() {
    local extension_point="${1:-}"

    if [[ -z "$extension_point" ]]; then
        platform_log_error "Extension point name not informed."
        return 1
    fi

    if ! platform_module_extension_is_registered "$extension_point"; then
        platform_log_error "Unknown extension point: $extension_point"
        return 1
    fi

    if [[ -z "${PLATFORM_MODULE_EXTENSION_PROVIDER_FUNCTIONS[$extension_point]+x}" ]]; then
        platform_log_error "No provider function registered for extension point: $extension_point"
        return 1
    fi

    printf '%s\n' "${PLATFORM_MODULE_EXTENSION_PROVIDER_FUNCTIONS[$extension_point]}"
}

#
# Lista todos os Extension Points registrados.
#
platform_module_extension_list() {
    local extension_point

    for extension_point in "${!PLATFORM_MODULE_EXTENSION_POINTS[@]}"; do
        printf '%s\n' "$extension_point"
    done
}

#
# Lista os Providers registrados.
#
# Formato:
#
# extension_point:provider_module:provider_function
#
platform_module_extension_list_providers() {
    local extension_point

    for extension_point in "${!PLATFORM_MODULE_EXTENSION_PROVIDERS[@]}"; do
        printf '%s:%s:%s\n' \
            "$extension_point" \
            "${PLATFORM_MODULE_EXTENSION_PROVIDERS[$extension_point]}" \
            "${PLATFORM_MODULE_EXTENSION_PROVIDER_FUNCTIONS[$extension_point]}"
    done
}