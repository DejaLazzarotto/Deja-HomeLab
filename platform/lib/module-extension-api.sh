#!/usr/bin/env bash

#
# ==========================================================
# Deja Platform
# Module Extension Public API
# ==========================================================
#

#
# Registra um Extension Point.
#
platform_register_extension_point() {
    local extension_point="${1:-}"

    platform_module_extension_register "$extension_point"
}

#
# Registra um Provider para um Extension Point.
#
platform_register_extension_provider() {
    local extension_point="${1:-}"
    local provider_module="${2:-}"
    local provider_function="${3:-}"

    platform_module_extension_register_provider \
        "$extension_point" \
        "$provider_module" \
        "$provider_function"
}

#
# Executa o Provider registrado para um Extension Point.
#
# Todos os argumentos adicionais são encaminhados diretamente
# para a função responsável pelo Extension Point.
#
platform_execute_extension() {
    local extension_point="${1:-}"

    if [[ "$#" -gt 0 ]]; then
        shift
    fi

    platform_module_extension_dispatch \
        "$extension_point" \
        "$@"
}

#
# Verifica se um Extension Point está registrado.
#
platform_has_extension_point() {
    local extension_point="${1:-}"

    platform_module_extension_is_registered "$extension_point"
}

#
# Verifica se um Extension Point possui Provider registrado.
#
platform_has_extension_provider() {
    local extension_point="${1:-}"

    platform_module_extension_has_provider "$extension_point"
}

#
# Retorna o módulo provedor de um Extension Point.
#
platform_get_extension_provider() {
    local extension_point="${1:-}"

    platform_module_extension_get_provider "$extension_point"
}

#
# Lista todos os Extension Points registrados.
#
platform_list_extension_points() {
    platform_module_extension_list
}

#
# Lista todos os Extension Points que possuem Providers.
#
platform_list_extension_providers() {
    platform_module_extension_list_providers
}