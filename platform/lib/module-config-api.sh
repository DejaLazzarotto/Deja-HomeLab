#!/usr/bin/env bash

#
# ==========================================================
# Deja Platform
# Module Configuration Public API
# ==========================================================
#

#
# Registra uma configuração pública de um módulo.
#
platform_register_module_config() {
    local module="${1:-}"
    local config_key="${2:-}"
    local default_value="${3-}"

    [[ -z "$module" ]] && return 1
    [[ -z "$config_key" ]] && return 1

    platform_module_config_registry_register \
        "$module" \
        "$config_key" \
        "$default_value"
}

#
# Verifica se uma configuração está registrada.
#
platform_has_module_config() {
    local module="${1:-}"
    local config_key="${2:-}"

    [[ -z "$module" ]] && return 1
    [[ -z "$config_key" ]] && return 1

    platform_module_config_registry_has \
        "$module" \
        "$config_key"
}

#
# Retorna o valor atual de uma configuração.
#
platform_get_module_config() {
    local module="${1:-}"
    local config_key="${2:-}"

    [[ -z "$module" ]] && return 1
    [[ -z "$config_key" ]] && return 1

    platform_module_config_registry_get \
        "$module" \
        "$config_key"
}

#
# Retorna o valor padrão de uma configuração.
#
platform_get_module_default_config() {
    local module="${1:-}"
    local config_key="${2:-}"

    [[ -z "$module" ]] && return 1
    [[ -z "$config_key" ]] && return 1

    platform_module_config_registry_get_default \
        "$module" \
        "$config_key"
}

#
# Lista todas as configurações registradas por um módulo.
#
platform_list_module_configs() {
    local module="${1:-}"

    [[ -z "$module" ]] && return 1

    platform_module_config_registry_list "$module"
}

#
# Lista os módulos que possuem configurações registradas.
#
platform_list_module_configs_modules() {
    platform_module_config_registry_list_modules
}