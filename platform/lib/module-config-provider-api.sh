#!/usr/bin/env bash

#
# ==========================================================
# Deja Platform
# Module Configuration Provider Public API
# ==========================================================
#

#
# Provider padrão do Kernel.
#
# Resolve configurações utilizando a Module Configuration
# Public API já existente.
#
# Argumentos:
#
#   $1 - Nome do módulo.
#   $2 - Chave da configuração.
#
platform_module_config_provider_kernel_resolve() {
    local module="${1:-}"
    local key="${2:-}"

    if [[ -z "$module" ]]; then
        platform_log_error \
            "Module name not informed for configuration resolution."
        return 1
    fi

    if [[ -z "$key" ]]; then
        platform_log_error \
            "Configuration key not informed: module=$module"
        return 1
    fi

    platform_get_module_config "$module" "$key"
}

#
# Registra publicamente um provider de configuração.
#
# Argumentos:
#
#   $1 - Nome único do provider.
#   $2 - Função responsável pela resolução.
#
platform_register_module_config_provider() {
    local provider="${1:-}"
    local resolver_function="${2:-}"

    platform_module_config_provider_registry_register \
        "$provider" \
        "$resolver_function"
}

#
# Verifica se um provider de configuração está registrado.
#
platform_has_module_config_provider() {
    local provider="${1:-}"

    platform_module_config_provider_registry_has "$provider"
}

#
# Lista os providers de configuração registrados.
#
platform_list_module_config_providers() {
    platform_module_config_provider_registry_list
}

#
# Resolve uma configuração utilizando um provider específico.
#
# Argumentos:
#
#   $1 - Nome do provider.
#   $2 - Nome do módulo.
#   $3 - Chave da configuração.
#
platform_resolve_module_config_with_provider() {
    local provider="${1:-}"
    local module="${2:-}"
    local key="${3:-}"

    if [[ -z "$provider" ]]; then
        platform_log_error \
            "Configuration provider name not informed."
        return 1
    fi

    if [[ -z "$module" ]]; then
        platform_log_error \
            "Module name not informed for configuration resolution."
        return 1
    fi

    if [[ -z "$key" ]]; then
        platform_log_error \
            "Configuration key not informed: module=$module provider=$provider"
        return 1
    fi

    platform_module_config_provider_registry_resolve \
        "$provider" \
        "$module" \
        "$key"
}

#
# Resolve uma configuração através dos providers registrados,
# respeitando a ordem oficial de registro.
#
# O primeiro provider que resolver a configuração com sucesso
# encerra o encadeamento.
#
# Argumentos:
#
#   $1 - Nome do módulo.
#   $2 - Chave da configuração.
#
platform_resolve_module_config() {
    local module="${1:-}"
    local key="${2:-}"
    local provider
    local value

    if [[ -z "$module" ]]; then
        platform_log_error \
            "Module name not informed for configuration resolution."
        return 1
    fi

    if [[ -z "$key" ]]; then
        platform_log_error \
            "Configuration key not informed: module=$module"
        return 1
    fi

    while IFS= read -r provider; do
        [[ -z "$provider" ]] && continue

        if value="$(
            platform_module_config_provider_registry_resolve \
                "$provider" \
                "$module" \
                "$key"
        )"; then
            printf '%s\n' "$value"
            return 0
        fi
    done < <(platform_module_config_provider_registry_list)

    platform_log_error \
        "Module configuration could not be resolved: module=$module key=$key"

    return 1
}

#
# Registra os providers oficiais disponibilizados pelo Kernel.
#
platform_register_builtin_module_config_providers() {
    if ! platform_module_config_provider_registry_has "yaml"; then
        platform_module_config_provider_registry_register \
            "yaml" \
            "platform_module_config_provider_yaml_resolve"
    fi

    if ! platform_module_config_provider_registry_has "kernel"; then
        platform_module_config_provider_registry_register \
            "kernel" \
            "platform_module_config_provider_kernel_resolve"
    fi
}