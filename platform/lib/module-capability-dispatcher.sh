#!/usr/bin/env bash

#
# ==========================================================
# Deja Platform
# Module Capability Dispatcher
# Internal Kernel Implementation
# ==========================================================
#

#
# Executa uma Capability registrada.
#
platform_module_capability_dispatch() {
    local capability="${1:-}"
    local capability_function

    if [[ -z "$capability" ]]; then
        platform_log_error "Capability name not informed."
        return 1
    fi

    if ! platform_module_capability_exists "$capability"; then
        platform_log_error "Capability not registered: $capability"
        return 1
    fi

    capability_function="$(platform_module_capability_get_function "$capability")" || return 1

    if [[ -z "$capability_function" ]]; then
        platform_log_error \
            "Capability implementation not informed: $capability"
        return 1
    fi

    if ! declare -F "$capability_function" >/dev/null 2>&1; then
        platform_log_error \
            "Capability implementation function not found: $capability_function"
        return 1
    fi

    shift

    "$capability_function" "$@"
}