#!/usr/bin/env bash

#
# ==========================================================
# Deja Platform
# Module Configuration Observer Dispatcher
# Internal Kernel Implementation
# ==========================================================
#

#
# Verifica se um evento pertence ao contrato oficial
# de eventos de configuração.
#
# Argumentos:
#
#   $1 - Nome do evento.
#
platform_module_config_observer_event_is_supported() {
    local event="${1:-}"

    case "$event" in
        module.config.loaded|\
        module.config.invalidated|\
        module.config.reloaded|\
        module.config.refreshed)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

#
# Notifica sincronamente todos os Configuration Observers
# registrados.
#
# Argumentos:
#
#   $1 - Contexto estruturado do evento.
#
# Cada callback recebe o mesmo contexto produzido pelo
# Module Event Dispatcher.
#
# A ordem de execução corresponde à ordem de registro.
# A primeira falha interrompe imediatamente o dispatch.
#
platform_module_config_observer_dispatch() {
    local context="${1:-}"
    local event
    local observer
    local callback

    [[ -z "$context" ]] && return 1

    event="$(
        platform_module_event_context_get \
            "$context" \
            "event"
    )" || return 1

    platform_module_config_observer_event_is_supported \
        "$event" || return 1

    while IFS= read -r observer; do
    [[ -z "$observer" ]] && continue

    callback="$(
        platform_module_config_observer_registry_get_callback \
            "$observer"
    )" || return 1

    declare -F "$callback" >/dev/null || return 1

    "$callback" "$context" || return $?
done < <(
    platform_module_config_observer_registry_list
)
}

#
# Listener interno utilizado para integrar os Configuration
# Observers ao Module Event Dispatcher.
#
# Argumentos:
#
#   $1 - Contexto estruturado do evento.
#
platform_module_config_observer_event_listener() {
    local context="${1:-}"

    [[ -z "$context" ]] && return 1

    platform_module_config_observer_dispatch "$context"
}

#
# Registra o listener interno dos Configuration Observers
# nos eventos oficiais de configuração.
#
platform_module_config_observer_dispatcher_init() {
    local event

    for event in \
        "module.config.loaded" \
        "module.config.invalidated" \
        "module.config.reloaded" \
        "module.config.refreshed"; do

        platform_module_event_register \
            "$event" \
            "platform_module_config_observer_event_listener" || return 1
    done
}