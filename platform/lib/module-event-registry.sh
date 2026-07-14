#!/usr/bin/env bash

#
# ==========================================================
# Deja Platform
# Module Event Registry
# Internal Kernel Implementation
# ==========================================================
#

declare -gA PLATFORM_MODULE_EVENT_LISTENERS=()

platform_module_event_reset() {
    PLATFORM_MODULE_EVENT_LISTENERS=()
}

platform_module_event_register() {
    local event="${1:-}"
    local listener="${2:-}"
    local current

    [[ -z "$event" ]] && return 1
    [[ -z "$listener" ]] && return 1

    case "$event" in
        module.before_bootstrap|module.after_bootstrap|module.bootstrap_failed)
            ;;
        *)
            return 1
            ;;
    esac

    declare -F "$listener" >/dev/null || return 1

    current="${PLATFORM_MODULE_EVENT_LISTENERS[$event]}"

    if [[ -z "$current" ]]; then
        PLATFORM_MODULE_EVENT_LISTENERS["$event"]="$listener"
    else
        PLATFORM_MODULE_EVENT_LISTENERS["$event"]="$current"$'\n'"$listener"
    fi
}

platform_module_event_has_listeners() {
    local event="${1:-}"

    [[ -n "${PLATFORM_MODULE_EVENT_LISTENERS[$event]:-}" ]]
}

platform_module_event_emit() {
    local event="${1:-}"

    shift || true

    local listeners
    local listener

    listeners="${PLATFORM_MODULE_EVENT_LISTENERS[$event]:-}"

    [[ -z "$listeners" ]] && return 0

    while IFS= read -r listener; do
        [[ -z "$listener" ]] && continue

        "$listener" "$@" || return $?
    done <<< "$listeners"
}