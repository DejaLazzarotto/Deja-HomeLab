#!/usr/bin/env bash

#
# ==========================================================
# Deja Platform
# Capability Public API
# ==========================================================
#

#
# Registra uma Capability fornecida por um módulo.
#
platform_register_capability() {
    local module="${1:-}"
    local capability="${2:-}"
    local function="${3:-}"

    platform_module_capability_register \
        "$module" \
        "$capability" \
        "$function"
}

#
# Executa uma Capability registrada.
#
# Todos os argumentos adicionais são encaminhados diretamente
# para a função responsável pela Capability.
#
platform_execute_capability() {
    local capability="${1:-}"

    if [[ "$#" -gt 0 ]]; then
        shift
    fi

    platform_module_capability_dispatch \
        "$capability" \
        "$@"
}

#
# Verifica se uma Capability está registrada.
#
platform_has_capability() {
    local capability="${1:-}"

    platform_module_capability_exists "$capability"
}

#
# Retorna o módulo provedor de uma Capability.
#
platform_get_capability_provider() {
    local capability="${1:-}"

    platform_module_capability_get_module "$capability"
}

#
# Lista todas as Capabilities registradas.
#
platform_list_capabilities() {
    platform_module_capability_registry_list
}