#!/usr/bin/env bash

#
# ==========================================================
# Deja Platform
# Module Extension Point Dispatcher
# Internal Kernel Implementation
# ==========================================================
#

#
# Verifica se um Extension Point possui Provider registrado.
#
platform_module_extension_has_provider() {
    local extension_point="${1:-}"

    if [[ -z "$extension_point" ]]; then
        platform_log_error "Extension point name not informed."
        return 1
    fi

    if ! platform_module_extension_is_registered "$extension_point"; then
        platform_log_error "Unknown extension point: $extension_point"
        return 1
    fi

    platform_module_extension_provider_is_registered "$extension_point"
}

#
# Resolve a função Provider associada a um Extension Point.
#
platform_module_extension_resolve() {
    local extension_point="${1:-}"
    local provider_function

    if [[ -z "$extension_point" ]]; then
        platform_log_error "Extension point name not informed."
        return 1
    fi

    provider_function="$(
        platform_module_extension_get_provider_function "$extension_point"
    )" || return 1

    if ! declare -F "$provider_function" >/dev/null 2>&1; then
        platform_log_error \
            "Extension provider function is no longer available: $provider_function"
        return 1
    fi

    printf '%s\n' "$provider_function"
}

#
# Executa o Provider registrado para um Extension Point.
#
# Todos os argumentos adicionais são encaminhados diretamente
# para a função Provider.
#
platform_module_extension_dispatch() {
    local extension_point="${1:-}"
    local provider_function

    if [[ -z "$extension_point" ]]; then
        platform_log_error "Extension point name not informed."
        return 1
    fi

    shift

    provider_function="$(
        platform_module_extension_resolve "$extension_point"
    )" || return 1

    "$provider_function" "$@"
}