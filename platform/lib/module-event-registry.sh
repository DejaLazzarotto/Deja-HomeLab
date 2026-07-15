#!/usr/bin/env bash

#
# ==========================================================
# Deja Platform
# Module Event Registry
# Internal Kernel Implementation
# ==========================================================
#

declare -gA PLATFORM_MODULE_EVENT_LISTENERS=()

#
# Limpa completamente o registro de listeners internos.
#
platform_module_event_reset() {
    PLATFORM_MODULE_EVENT_LISTENERS=()
}

#
# Verifica se um evento pertence ao contrato interno
# de eventos da plataforma.
#
platform_module_event_is_supported() {
    local event="${1:-}"

    case "$event" in
        module.before_bootstrap|\
        module.after_bootstrap|\
        module.bootstrap_failed|\
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
# Registra um listener interno para um evento suportado.
#
platform_module_event_register() {
    local event="${1:-}"
    local listener="${2:-}"
    local current

    [[ -z "$event" ]] && return 1
    [[ -z "$listener" ]] && return 1

    platform_module_event_is_supported "$event" || return 1

    declare -F "$listener" >/dev/null || return 1

    current="${PLATFORM_MODULE_EVENT_LISTENERS[$event]:-}"

    if [[ -z "$current" ]]; then
        PLATFORM_MODULE_EVENT_LISTENERS["$event"]="$listener"
    else
        PLATFORM_MODULE_EVENT_LISTENERS["$event"]="$current"$'\n'"$listener"
    fi
}

#
# Verifica se um evento possui listeners registrados.
#
platform_module_event_has_listeners() {
    local event="${1:-}"

    [[ -z "$event" ]] && return 1

    platform_module_event_is_supported "$event" || return 1

    [[ -n "${PLATFORM_MODULE_EVENT_LISTENERS[$event]:-}" ]]
}

#
# Retorna os listeners registrados para um evento.
#
# A execução dos listeners pertence ao Event Dispatcher.
#
platform_module_event_list_listeners() {
    local event="${1:-}"

    [[ -z "$event" ]] && return 1

    platform_module_event_is_supported "$event" || return 1

    printf '%s\n' "${PLATFORM_MODULE_EVENT_LISTENERS[$event]:-}"
}

#
# API de compatibilidade.
#
# Quando o Event Dispatcher estiver carregado, toda emissão será
# delegada a ele. O fallback preserva temporariamente o comportamento
# anterior durante o bootstrap incremental do Kernel.
#
platform_module_event_emit() {
    local event="${1:-}"

    [[ -z "$event" ]] && return 1

    platform_module_event_is_supported "$event" || return 1

    shift || true

    if declare -F platform_module_event_dispatch >/dev/null; then
        platform_module_event_dispatch "$event" "$@"
        return $?
    fi

    local listeners
    local listener

    listeners="${PLATFORM_MODULE_EVENT_LISTENERS[$event]:-}"

    [[ -z "$listeners" ]] && return 0

    while IFS= read -r listener; do
        [[ -z "$listener" ]] && continue

        "$listener" "$@" || return $?
    done <<< "$listeners"
}