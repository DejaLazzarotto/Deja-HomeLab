#!/usr/bin/env bash

#
# ==========================================================
# Deja Platform
# Module Hook Dispatcher
# Internal Kernel Implementation
# ==========================================================
#

#
# Executa os Hooks registrados para um ponto específico.
#
# Contrato interno do Hook:
#
#   $1 = nome do módulo
#   $2 = nome do Hook
#   $3 = estado atual do módulo
#
platform_module_hook_dispatch() {
    local hook_name="${1:-}"
    local module="${2:-}"
    local lifecycle_state="${3:-}"

    local hook_function
    local hook_status

    if [[ -z "$hook_name" ]]; then
        platform_log_error "Module hook name not informed for dispatch."
        return 1
    fi

    if [[ -z "$module" ]]; then
        platform_log_error "Module name not informed for hook dispatch."
        return 1
    fi

    if [[ -z "$lifecycle_state" ]]; then
        platform_log_error "Module lifecycle state not informed for hook dispatch."
        return 1
    fi

    if ! platform_module_hook_registry_is_supported "$hook_name"; then
        platform_log_error "Unsupported module hook dispatch: $hook_name"
        return 1
    fi

    while IFS= read -r hook_function; do
        [[ -z "$hook_function" ]] && continue

        if ! declare -F "$hook_function" >/dev/null; then
            platform_log_error \
                "Registered module hook function not found: hook=$hook_name function=$hook_function"
            return 1
        fi

        "$hook_function" "$module" "$hook_name" "$lifecycle_state"
        hook_status=$?

        if (( hook_status != 0 )); then
            platform_log_error \
                "Module hook execution failed: hook=$hook_name module=$module function=$hook_function status=$hook_status"
            return "$hook_status"
        fi
    done < <(platform_module_hook_registry_list "$hook_name")

    return 0
}