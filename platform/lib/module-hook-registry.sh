#!/usr/bin/env bash

#
# ==========================================================
# Deja Platform
# Module Hook Registry
# Internal Kernel Implementation
# ==========================================================
#

declare -gA PLATFORM_MODULE_HOOKS=()

#
# Limpa completamente o registro interno de Hooks.
#
platform_module_hook_registry_reset() {
    PLATFORM_MODULE_HOOKS=()
}

#
# Verifica se um Hook é suportado pelo Kernel.
#
platform_module_hook_registry_is_supported() {
    local hook_name="${1:-}"

    case "$hook_name" in
        module.before_bootstrap|module.after_bootstrap)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

#
# Registra uma função em um Hook.
#
platform_module_hook_registry_register() {
    local hook_name="${1:-}"
    local hook_function="${2:-}"

    local registered_hooks
    local registered_function

    [[ -z "$hook_name" ]] && {
        platform_log_error "Module hook name not informed."
        return 1
    }

    [[ -z "$hook_function" ]] && {
        platform_log_error "Module hook function not informed."
        return 1
    }

    if ! platform_module_hook_registry_is_supported "$hook_name"; then
        platform_log_error "Unsupported module hook: $hook_name"
        return 1
    fi

    if ! declare -F "$hook_function" >/dev/null; then
        platform_log_error "Module hook function not found: $hook_function"
        return 1
    fi

    registered_hooks="${PLATFORM_MODULE_HOOKS[$hook_name]:-}"

    while IFS= read -r registered_function; do
        [[ -z "$registered_function" ]] && continue

        if [[ "$registered_function" == "$hook_function" ]]; then
            platform_log_error \
                "Module hook already registered: hook=$hook_name function=$hook_function"
            return 1
        fi
    done <<< "$registered_hooks"

    if [[ -z "$registered_hooks" ]]; then
        PLATFORM_MODULE_HOOKS["$hook_name"]="$hook_function"
    else
        PLATFORM_MODULE_HOOKS["$hook_name"]+=$'\n'"$hook_function"
    fi
}

#
# Lista os Hooks registrados.
#
platform_module_hook_registry_list() {
    local hook_name="${1:-}"

    [[ -z "$hook_name" ]] && {
        platform_log_error "Module hook name not informed."
        return 1
    }

    if ! platform_module_hook_registry_is_supported "$hook_name"; then
        platform_log_error "Unsupported module hook: $hook_name"
        return 1
    fi

    [[ -n "${PLATFORM_MODULE_HOOKS[$hook_name]:-}" ]] || return 0

    printf '%s\n' "${PLATFORM_MODULE_HOOKS[$hook_name]}"
}