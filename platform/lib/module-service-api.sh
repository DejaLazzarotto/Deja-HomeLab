#!/usr/bin/env bash

#
# ==========================================================
# Deja Platform
# Module Service Public API
# ==========================================================
#

#
# Registra um Service fornecido por um módulo.
#
platform_register_service() {
    local module="${1:-}"
    local service="${2:-}"
    local function="${3:-}"

    platform_module_service_register \
        "$module" \
        "$service" \
        "$function"
}

#
# Resolve e executa um Service registrado.
#
# Todos os argumentos adicionais são encaminhados diretamente
# para a função responsável pelo Service.
#
platform_resolve_service() {
    local service="${1:-}"

    if [[ "$#" -gt 0 ]]; then
        shift
    fi

    platform_module_service_dispatch \
        "$service" \
        "$@"
}

#
# Verifica se um Service está registrado.
#
platform_has_service() {
    local service="${1:-}"

    platform_module_service_exists "$service"
}

#
# Retorna o módulo provedor de um Service.
#
platform_get_service_provider() {
    local service="${1:-}"

    platform_module_service_get_module "$service"
}

#
# Lista todos os Services registrados.
#
platform_list_services() {
    platform_module_service_registry_list
}