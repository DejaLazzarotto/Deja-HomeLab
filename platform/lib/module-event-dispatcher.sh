#!/usr/bin/env bash

#
# ==========================================================
# Deja Platform
# Module Event Dispatcher
# Internal Kernel Implementation
# ==========================================================
#

#
# Gera um timestamp UTC padronizado para os eventos internos.
#
platform_module_event_timestamp() {
    date -u +"%Y-%m-%dT%H:%M:%SZ"
}

#
# Constrói o contexto estruturado de um evento.
#
platform_module_event_context_build() {
    local event="${1:-}"
    local module="${2:-}"
    local lifecycle_state="${3:-}"
    local status="${4:-}"
    local message="${5:-}"
    local timestamp

    [[ -z "$event" ]] && return 1
    [[ -z "$module" ]] && return 1

    platform_module_event_is_supported "$event" || return 1

    timestamp="$(platform_module_event_timestamp)" || return 1

    printf '%s\n' \
        "event=$event" \
        "module=$module" \
        "timestamp=$timestamp" \
        "lifecycle_state=$lifecycle_state" \
        "status=$status" \
        "message=$message"
}

#
# Retorna um campo do contexto estruturado.
#
platform_module_event_context_get() {
    local context="${1:-}"
    local field="${2:-}"
    local line

    [[ -z "$field" ]] && return 1

    while IFS= read -r line; do
        case "$line" in
            "$field="*)
                printf '%s\n' "${line#*=}"
                return 0
                ;;
        esac
    done <<< "$context"

    return 1
}

#
# Listener interno responsável pelo logging dos eventos.
#
platform_module_event_logging_listener() {
    local context="${1:-}"
    local event
    local module
    local lifecycle_state
    local status
    local message
    local log_message

    [[ -z "$context" ]] && return 1

    event="$(platform_module_event_context_get "$context" "event")" || return 1
    module="$(platform_module_event_context_get "$context" "module")" || return 1
    lifecycle_state="$(platform_module_event_context_get "$context" "lifecycle_state")" || true
    status="$(platform_module_event_context_get "$context" "status")" || true
    message="$(platform_module_event_context_get "$context" "message")" || true

    log_message="Module lifecycle event: event=$event module=$module"

    [[ -n "$lifecycle_state" ]] && \
        log_message+=" lifecycle_state=$lifecycle_state"

    [[ -n "$status" ]] && \
        log_message+=" status=$status"

    [[ -n "$message" ]] && \
        log_message+=" message=$message"

    case "$event" in
        module.bootstrap_failed)
            platform_log_error "$log_message"
            ;;
        *)
            platform_log_info "$log_message"
            ;;
    esac
}

#
# Registra os listeners internos padrão do Dispatcher.
#
platform_module_event_dispatcher_init() {
    platform_module_event_register \
        "module.before_bootstrap" \
        "platform_module_event_logging_listener" || return 1

    platform_module_event_register \
        "module.after_bootstrap" \
        "platform_module_event_logging_listener" || return 1

    platform_module_event_register \
        "module.bootstrap_failed" \
        "platform_module_event_logging_listener" || return 1
}

#
# Despacha um evento para todos os listeners internos registrados.
#
platform_module_event_dispatch() {
    local event="${1:-}"
    local module="${2:-}"
    local lifecycle_state="${3:-}"
    local status="${4:-}"
    local message="${5:-}"
    local context
    local listeners
    local listener

    [[ -z "$event" ]] && return 1
    [[ -z "$module" ]] && return 1

    platform_module_event_is_supported "$event" || return 1

    context="$(
        platform_module_event_context_build \
            "$event" \
            "$module" \
            "$lifecycle_state" \
            "$status" \
            "$message"
    )" || return 1

    listeners="$(platform_module_event_list_listeners "$event")" || return 1

    [[ -z "$listeners" ]] && return 0

    while IFS= read -r listener; do
        [[ -z "$listener" ]] && continue

        "$listener" "$context" || return $?
    done <<< "$listeners"
}