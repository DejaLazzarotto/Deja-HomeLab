#!/usr/bin/env bash

#
# ==========================================================
# Deja Platform
# Module Configuration Observer Registry
# Internal Kernel Implementation
# ==========================================================
#

#
# Callbacks registrados, indexados pelo nome único do observer.
#
declare -gA PLATFORM_MODULE_CONFIG_OBSERVER_CALLBACKS=()

#
# Ordem oficial de registro dos observers.
#
# A ordem é preservada para garantir notificação síncrona
# determinística.
#
declare -ga PLATFORM_MODULE_CONFIG_OBSERVERS=()

#
# Limpa completamente o registro de Configuration Observers.
#
platform_module_config_observer_registry_reset() {
    PLATFORM_MODULE_CONFIG_OBSERVER_CALLBACKS=()
    PLATFORM_MODULE_CONFIG_OBSERVERS=()
}

#
# Verifica se um observer está registrado.
#
# Argumentos:
#
#   $1 - Nome único do observer.
#
platform_module_config_observer_registry_has() {
    local observer="${1:-}"

    [[ -z "$observer" ]] && return 1

    [[ -n "${PLATFORM_MODULE_CONFIG_OBSERVER_CALLBACKS[$observer]+x}" ]]
}

#
# Registra um Configuration Observer.
#
# Argumentos:
#
#   $1 - Nome único do observer.
#   $2 - Função callback responsável pela notificação.
#
# O callback deve existir no momento do registro.
#
platform_module_config_observer_registry_register() {
    local observer="${1:-}"
    local callback="${2:-}"

    [[ -z "$observer" ]] && return 1
    [[ -z "$callback" ]] && return 1

    declare -F "$callback" >/dev/null || return 1

    if platform_module_config_observer_registry_has "$observer"; then
        return 1
    fi

    PLATFORM_MODULE_CONFIG_OBSERVER_CALLBACKS["$observer"]="$callback"
    PLATFORM_MODULE_CONFIG_OBSERVERS+=("$observer")
}

#
# Remove um Configuration Observer.
#
# Argumentos:
#
#   $1 - Nome único do observer.
#
platform_module_config_observer_registry_unregister() {
    local observer="${1:-}"
    local registered_observer
    local -a remaining_observers=()

    [[ -z "$observer" ]] && return 1

    platform_module_config_observer_registry_has "$observer" || return 1

    for registered_observer in "${PLATFORM_MODULE_CONFIG_OBSERVERS[@]}"; do
        if [[ "$registered_observer" != "$observer" ]]; then
            remaining_observers+=("$registered_observer")
        fi
    done

    unset 'PLATFORM_MODULE_CONFIG_OBSERVER_CALLBACKS[$observer]'
    PLATFORM_MODULE_CONFIG_OBSERVERS=("${remaining_observers[@]}")
}

#
# Retorna o callback associado a um observer.
#
# Argumentos:
#
#   $1 - Nome único do observer.
#
platform_module_config_observer_registry_get_callback() {
    local observer="${1:-}"

    [[ -z "$observer" ]] && return 1

    platform_module_config_observer_registry_has "$observer" || return 1

    printf '%s\n' \
        "${PLATFORM_MODULE_CONFIG_OBSERVER_CALLBACKS[$observer]}"
}

#
# Lista os observers na ordem em que foram registrados.
#
platform_module_config_observer_registry_list() {
    local observer

    for observer in "${PLATFORM_MODULE_CONFIG_OBSERVERS[@]}"; do
        printf '%s\n' "$observer"
    done
}