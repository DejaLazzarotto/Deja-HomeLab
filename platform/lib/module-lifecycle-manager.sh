#!/usr/bin/env bash

#
# ==========================================================
# Deja Platform
# Module Lifecycle Manager
# Internal Kernel Implementation
# ==========================================================
#

#
# Executa o bootstrap individual de um módulo.
#
# O módulo deve estar no estado LOADED.
# Quando o bootstrap for concluído, seu estado será atualizado
# automaticamente para BOOTSTRAPPED.
#
platform_module_lifecycle_bootstrap_module() {
    local module="${1:-}"
    local current_state
    local bootstrap_function

    if [[ -z "$module" ]]; then
        platform_log_error "Module name not informed for bootstrap."
        return 1
    fi

    current_state="$(platform_module_state_get "$module")" || return 1

    if [[ "$current_state" == "BOOTSTRAPPED" ]]; then
        return 0
    fi

    if [[ "$current_state" != "LOADED" ]]; then
        platform_log_error \
            "Module '$module' cannot be bootstrapped from state '$current_state'."
        return 1
    fi

    bootstrap_function="platform_module_${module//-/_}_bootstrap"

    if declare -F "$bootstrap_function" >/dev/null 2>&1; then
        "$bootstrap_function" || {
            platform_log_error "Module bootstrap failed: $module"
            return 1
        }
    fi

    platform_module_state_set "$module" "BOOTSTRAPPED" || return 1
}

#
# Executa o bootstrap de todos os módulos resolvidos.
#
# A ordem fornecida pelo Dependency Resolver é preservada.
#
platform_module_lifecycle_bootstrap_all() {
    local module
    local modules=()

    mapfile -t modules < <(platform_dependency_resolver_list)

    if [[ "${#modules[@]}" -eq 0 ]]; then
        platform_log_error "No resolved modules available for bootstrap."
        return 1
    fi

    for module in "${modules[@]}"; do
        platform_module_lifecycle_bootstrap_module "$module" || return 1
    done
}