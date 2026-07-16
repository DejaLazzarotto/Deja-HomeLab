#!/usr/bin/env bash

#
# ==========================================================
# Deja Platform
# Module Configuration Observer Public API
# ==========================================================
#

#
# Registra um Configuration Observer pertencente a um módulo.
#
# Argumentos:
#
#   $1 - Nome do módulo proprietário.
#   $2 - Nome único do observer.
#   $3 - Função callback responsável pela notificação.
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
platform_module_config_observer_register() {
    local module="${1:-}"
    local observer="${2:-}"
    local callback="${3:-}"

    if [[ -z "$module" ]]; then
        platform_log_error \
            "Module name not informed for configuration observer registration."
        return 1
    fi

    if [[ -z "$observer" ]]; then
        platform_log_error \
            "Configuration observer name not informed: module=$module"
        return 1
    fi

    if [[ -z "$callback" ]]; then
        platform_log_error \
            "Configuration observer callback not informed: module=$module observer=$observer"
        return 1
    fi

    if ! declare -F "$callback" >/dev/null; then
        platform_log_error \
            "Configuration observer callback does not exist: module=$module observer=$observer callback=$callback"
        return 1
    fi

    if platform_module_config_observer_registry_has "$observer"; then
        platform_log_error \
            "Configuration observer is already registered: observer=$observer"
        return 1
    fi

    platform_module_config_observer_registry_register \
        "$module" \
        "$observer" \
        "$callback"
}

#
# Remove um Configuration Observer pertencente a um módulo.
#
# Argumentos:
#
#   $1 - Nome do módulo proprietário.
#   $2 - Nome único do observer.
#
platform_module_config_observer_unregister() {
    local module="${1:-}"
    local observer="${2:-}"
    local registered_module

    if [[ -z "$module" ]]; then
        platform_log_error \
            "Module name not informed for configuration observer removal."
        return 1
    fi

    if [[ -z "$observer" ]]; then
        platform_log_error \
            "Configuration observer name not informed: module=$module"
        return 1
    fi

    if ! platform_module_config_observer_registry_has "$observer"; then
        platform_log_error \
            "Configuration observer is not registered: observer=$observer"
        return 1
    fi

    registered_module="$(
        platform_module_config_observer_registry_get_module \
            "$observer"
    )" || return 1

    if [[ "$registered_module" != "$module" ]]; then
        platform_log_error \
            "Configuration observer does not belong to module: observer=$observer module=$module registered_module=$registered_module"
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
platform_module_config_observer_exists() {
    local observer="${1:-}"

    [[ -z "$observer" ]] && return 1

    platform_module_config_observer_registry_has "$observer"
}

#
# Retorna o módulo proprietário de um Configuration Observer.
#
# Argumentos:
#
#   $1 - Nome único do observer.
#
platform_module_config_observer_get_module() {
    local observer="${1:-}"

    [[ -z "$observer" ]] && return 1

    platform_module_config_observer_registry_get_module \
        "$observer"
}

#
# Retorna o callback associado a um Configuration Observer.
#
# Argumentos:
#
#   $1 - Nome único do observer.
#
platform_module_config_observer_get_callback() {
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
platform_module_config_observer_list() {
    platform_module_config_observer_registry_list
}

#
# Lista os Configuration Observers pertencentes a um módulo.
#
# Argumentos:
#
#   $1 - Nome do módulo.
#
platform_module_config_observer_list_by_module() {
    local module="${1:-}"

    [[ -z "$module" ]] && return 1

    platform_module_config_observer_registry_list_by_module \
        "$module"
}

#
# Registra publicamente um Configuration Observer interno.
#
# Esta função preserva o contrato introduzido anteriormente.
# Observers registrados através dela pertencem ao Kernel.
#
# Argumentos:
#
#   $1 - Nome único do observer.
#   $2 - Função callback responsável pela notificação.
#
platform_register_module_config_observer() {
    local observer="${1:-}"
    local callback="${2:-}"

    platform_module_config_observer_register \
        "kernel" \
        "$observer" \
        "$callback"
}

#
# Remove publicamente um Configuration Observer interno.
#
# Esta função preserva o contrato introduzido anteriormente.
#
# Argumentos:
#
#   $1 - Nome único do observer.
#
platform_unregister_module_config_observer() {
    local observer="${1:-}"

    platform_module_config_observer_unregister \
        "kernel" \
        "$observer"
}

#
# Verifica se um Configuration Observer está registrado.
#
# Função de compatibilidade com o contrato anterior.
#
platform_has_module_config_observer() {
    local observer="${1:-}"

    platform_module_config_observer_exists "$observer"
}

#
# Retorna o callback associado a um Configuration Observer.
#
# Função de compatibilidade com o contrato anterior.
#
platform_get_module_config_observer_callback() {
    local observer="${1:-}"

    platform_module_config_observer_get_callback \
        "$observer"
}

#
# Lista os Configuration Observers registrados.
#
# Função de compatibilidade com o contrato anterior.
#
platform_list_module_config_observers() {
    platform_module_config_observer_list
}