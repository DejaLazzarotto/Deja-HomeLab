#!/usr/bin/env bash

#
# ==========================================================
# Deja Platform
# Module Configuration Observer Public API
# ==========================================================
#

#
# Registra publicamente um Configuration Observer.
#
# Argumentos:
#
#   $1 - Nome único do observer.
#   $2 - Função callback responsável pela notificação.
#
# Contrato do callback:
#
#   callback "$context"
#
# O callback recebe um único argumento contendo o contexto
# estruturado produzido pelo Module Event Dispatcher.
#
# O contexto pode ser consultado através da Module Event
# Context API, utilizando platform_module_event_context_get.
#
# Eventos atualmente observáveis:
#
#   module.config.loaded
#   module.config.invalidated
#   module.config.reloaded
#   module.config.refreshed
#
# Os observers são executados:
#
#   - sincronamente;
#   - na ordem em que foram registrados;
#   - até que todos sejam concluídos com sucesso;
#   - interrompendo o dispatch na primeira falha.
#
# O callback deve existir no momento do registro.
#
platform_register_module_config_observer() {
    local observer="${1:-}"
    local callback="${2:-}"

    if [[ -z "$observer" ]]; then
        platform_log_error \
            "Configuration observer name not informed."
        return 1
    fi

    if [[ -z "$callback" ]]; then
        platform_log_error \
            "Configuration observer callback not informed: observer=$observer"
        return 1
    fi

    if ! declare -F "$callback" >/dev/null; then
        platform_log_error \
            "Configuration observer callback does not exist: observer=$observer callback=$callback"
        return 1
    fi

    if platform_module_config_observer_registry_has "$observer"; then
        platform_log_error \
            "Configuration observer is already registered: observer=$observer"
        return 1
    fi

    platform_module_config_observer_registry_register \
        "$observer" \
        "$callback"
}

#
# Remove publicamente um Configuration Observer.
#
# Argumentos:
#
#   $1 - Nome único do observer.
#
platform_unregister_module_config_observer() {
    local observer="${1:-}"

    if [[ -z "$observer" ]]; then
        platform_log_error \
            "Configuration observer name not informed."
        return 1
    fi

    if ! platform_module_config_observer_registry_has "$observer"; then
        platform_log_error \
            "Configuration observer is not registered: observer=$observer"
        return 1
    fi

    platform_module_config_observer_registry_unregister \
        "$observer"
}

#
# Verifica se um Configuration Observer está registrado.
#
# Argumentos:
#
#   $1 - Nome único do observer.
#
platform_has_module_config_observer() {
    local observer="${1:-}"

    [[ -z "$observer" ]] && return 1

    platform_module_config_observer_registry_has "$observer"
}

#
# Retorna o callback associado a um Configuration Observer.
#
# Argumentos:
#
#   $1 - Nome único do observer.
#
platform_get_module_config_observer_callback() {
    local observer="${1:-}"

    [[ -z "$observer" ]] && return 1

    platform_module_config_observer_registry_get_callback \
        "$observer"
}

#
# Lista os Configuration Observers registrados.
#
# A listagem preserva a ordem oficial de registro.
#
platform_list_module_config_observers() {
    platform_module_config_observer_registry_list
}