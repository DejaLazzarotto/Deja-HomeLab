#!/usr/bin/env bash

#
# ==========================================================
# Deja Platform
# Module Configuration Registry
# Internal Kernel Implementation
# ==========================================================
#

declare -gA PLATFORM_MODULE_CONFIG_VALUES=()
declare -gA PLATFORM_MODULE_CONFIG_DEFAULTS=()
declare -gA PLATFORM_MODULE_CONFIG_MODULES=()

#
# Limpa completamente o registro interno de configurações.
#
platform_module_config_registry_reset() {
    PLATFORM_MODULE_CONFIG_VALUES=()
    PLATFORM_MODULE_CONFIG_DEFAULTS=()
    PLATFORM_MODULE_CONFIG_MODULES=()
}

#
# Gera a chave interna utilizada pelo Registry.
#
# Formato:
#
# module::config_key
#
platform_module_config_registry_build_key() {
    local module="${1:-}"
    local config_key="${2:-}"

    [[ -z "$module" ]] && return 1
    [[ -z "$config_key" ]] && return 1

    printf '%s::%s\n' "$module" "$config_key"
}

#
# Registra uma configuração de módulo.
#
# O valor informado será armazenado como valor atual e também
# como valor padrão da configuração.
#
platform_module_config_registry_register() {
    local module="${1:-}"
    local config_key="${2:-}"
    local default_value="${3-}"
    local registry_key

    [[ -z "$module" ]] && return 1
    [[ -z "$config_key" ]] && return 1

    registry_key="$(
        platform_module_config_registry_build_key \
            "$module" \
            "$config_key"
    )" || return 1

    if [[ -v "PLATFORM_MODULE_CONFIG_DEFAULTS[$registry_key]" ]]; then
        return 1
    fi

    PLATFORM_MODULE_CONFIG_DEFAULTS["$registry_key"]="$default_value"
    PLATFORM_MODULE_CONFIG_VALUES["$registry_key"]="$default_value"
    PLATFORM_MODULE_CONFIG_MODULES["$module"]="true"
}

#
# Verifica se uma configuração está registrada.
#
platform_module_config_registry_has() {
    local module="${1:-}"
    local config_key="${2:-}"
    local registry_key

    [[ -z "$module" ]] && return 1
    [[ -z "$config_key" ]] && return 1

    registry_key="$(
        platform_module_config_registry_build_key \
            "$module" \
            "$config_key"
    )" || return 1

    [[ -v "PLATFORM_MODULE_CONFIG_DEFAULTS[$registry_key]" ]]
}

#
# Retorna o valor atual de uma configuração.
#
platform_module_config_registry_get() {
    local module="${1:-}"
    local config_key="${2:-}"
    local registry_key

    [[ -z "$module" ]] && return 1
    [[ -z "$config_key" ]] && return 1

    registry_key="$(
        platform_module_config_registry_build_key \
            "$module" \
            "$config_key"
    )" || return 1

    [[ -v "PLATFORM_MODULE_CONFIG_VALUES[$registry_key]" ]] || return 1

    printf '%s\n' "${PLATFORM_MODULE_CONFIG_VALUES[$registry_key]}"
}

#
# Retorna o valor padrão de uma configuração.
#
platform_module_config_registry_get_default() {
    local module="${1:-}"
    local config_key="${2:-}"
    local registry_key

    [[ -z "$module" ]] && return 1
    [[ -z "$config_key" ]] && return 1

    registry_key="$(
        platform_module_config_registry_build_key \
            "$module" \
            "$config_key"
    )" || return 1

    [[ -v "PLATFORM_MODULE_CONFIG_DEFAULTS[$registry_key]" ]] || return 1

    printf '%s\n' "${PLATFORM_MODULE_CONFIG_DEFAULTS[$registry_key]}"
}

#
# Atualiza internamente o valor atual de uma configuração.
#
# Esta função será utilizada futuramente por providers e
# mecanismos de override. Ela não constitui uma API pública.
#
platform_module_config_registry_set() {
    local module="${1:-}"
    local config_key="${2:-}"
    local value="${3-}"
    local registry_key

    [[ -z "$module" ]] && return 1
    [[ -z "$config_key" ]] && return 1

    registry_key="$(
        platform_module_config_registry_build_key \
            "$module" \
            "$config_key"
    )" || return 1

    [[ -v "PLATFORM_MODULE_CONFIG_DEFAULTS[$registry_key]" ]] || return 1

    PLATFORM_MODULE_CONFIG_VALUES["$registry_key"]="$value"
}

#
# Lista as chaves de configuração registradas para um módulo.
#
platform_module_config_registry_list() {
    local module="${1:-}"
    local registry_key
    local prefix
    local config_key
    local -a config_keys=()

    [[ -z "$module" ]] && return 1

    prefix="${module}::"

    for registry_key in "${!PLATFORM_MODULE_CONFIG_DEFAULTS[@]}"; do
        [[ "$registry_key" == "$prefix"* ]] || continue

        config_key="${registry_key#"$prefix"}"
        config_keys+=("$config_key")
    done

    if (( ${#config_keys[@]} == 0 )); then
        return 0
    fi

    printf '%s\n' "${config_keys[@]}" | sort
}

#
# Lista os módulos que possuem configurações registradas.
#
platform_module_config_registry_list_modules() {
    local module

    if (( ${#PLATFORM_MODULE_CONFIG_MODULES[@]} == 0 )); then
        return 0
    fi

    for module in "${!PLATFORM_MODULE_CONFIG_MODULES[@]}"; do
        printf '%s\n' "$module"
    done | sort
}