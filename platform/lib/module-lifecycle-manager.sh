#!/usr/bin/env bash

#
# ==========================================================
# Deja Platform
# Module Lifecycle Manager
# Internal Kernel Implementation
# ==========================================================
#

#
# Executa o estágio opcional de publicação dos recursos
# pertencentes a um módulo.
#
# Convenção oficial:
#
#   platform_module_<module>_register_resources
#
# Módulos legados que não implementam essa função permanecem
# totalmente compatíveis e concluem o estágio com sucesso.
#
# O estágio é executado somente uma vez por módulo durante o
# ciclo atual do Kernel. Isso permite repetir o bootstrap após
# falhas posteriores sem republicar recursos já registrados.
#
# Argumentos:
#
#   $1 - Nome do módulo.
#   $2 - Estado atual do módulo.
#
platform_module_lifecycle_register_resources() {
    local module="${1:-}"
    local current_state="${2:-}"
    local resource_registration_function
    local resource_registration_exit_code

    if [[ -z "$module" ]]; then
        platform_log_error \
            "Module name not informed for resource registration."

        return 1
    fi

    if [[ -z "$current_state" ]]; then
        platform_log_error \
            "Module lifecycle state not informed for resource registration: $module"

        return 1
    fi

    #
    # O Resource Registration é executado somente uma vez por
    # módulo durante o ciclo atual do Kernel.
    #
    # Caso o bootstrap tenha falhado depois da publicação dos
    # recursos, uma nova tentativa não repetirá os registros.
    #
    if platform_module_resource_registration_state_is_completed "$module"; then
        return 0
    fi

    if ! platform_module_event_emit \
        "module.before_register_resources" \
        "$module" \
        "$current_state" \
        "starting" \
        "Module resource registration is starting."; then

        platform_log_error \
            "Module before-register-resources event failed: $module"

        return 1
    fi

    resource_registration_function="platform_module_${module//-/_}_register_resources"

    if declare -F "$resource_registration_function" >/dev/null 2>&1; then
        "$resource_registration_function"
        resource_registration_exit_code=$?

        if [[ "$resource_registration_exit_code" -ne 0 ]]; then
            platform_log_error \
                "Module resource registration failed: $module"

            platform_module_event_emit \
                "module.resource_registration_failed" \
                "$module" \
                "$current_state" \
                "failed" \
                "Module resource registration exited with code $resource_registration_exit_code." \
                || true

            return "$resource_registration_exit_code"
        fi
    fi

    if ! platform_module_event_emit \
        "module.after_register_resources" \
        "$module" \
        "$current_state" \
        "success" \
        "Module resource registration completed successfully."; then

        platform_log_error \
            "Module after-register-resources event failed: $module"

        return 1
    fi

    #
    # O estágio somente é considerado concluído depois que:
    #
    #   1. a função de publicação retornou sucesso;
    #   2. o evento after_register_resources foi emitido;
    #   3. todos os listeners do evento concluíram com sucesso.
    #
    platform_module_resource_registration_state_mark_completed "$module" \
        || return 1

    return 0
}

#
# Executa o bootstrap individual de um módulo.
#
# O módulo deve estar no estado LOADED.
#
# Antes do bootstrap, o módulo passa pelo estágio oficial de
# Resource Registration. Quando o registro de recursos, o
# bootstrap, seus eventos e Hooks forem concluídos, seu estado
# será atualizado automaticamente para BOOTSTRAPPED.
#
platform_module_lifecycle_bootstrap_module() {
    local module="${1:-}"
    local current_state
    local bootstrap_function
    local bootstrap_exit_code
    local hook_exit_code

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

    platform_module_lifecycle_register_resources \
        "$module" \
        "$current_state" \
        || return $?

    if ! platform_module_event_emit \
        "module.before_bootstrap" \
        "$module" \
        "$current_state" \
        "starting" \
        "Module bootstrap is starting."; then

        platform_log_error \
            "Module before-bootstrap event failed: $module"

        return 1
    fi

    platform_module_hook_dispatch \
        "module.before_bootstrap" \
        "$module" \
        "$current_state"

    hook_exit_code=$?

    if [[ "$hook_exit_code" -ne 0 ]]; then
        platform_log_error \
            "Module before-bootstrap hook failed: $module"

        return "$hook_exit_code"
    fi

    bootstrap_function="platform_module_${module//-/_}_bootstrap"

    if declare -F "$bootstrap_function" >/dev/null 2>&1; then
        "$bootstrap_function"
        bootstrap_exit_code=$?

        if [[ "$bootstrap_exit_code" -ne 0 ]]; then
            platform_log_error "Module bootstrap failed: $module"

            platform_module_event_emit \
                "module.bootstrap_failed" \
                "$module" \
                "$current_state" \
                "failed" \
                "Module bootstrap exited with code $bootstrap_exit_code." \
                || true

            return "$bootstrap_exit_code"
        fi
    fi

    if ! platform_module_event_emit \
        "module.after_bootstrap" \
        "$module" \
        "BOOTSTRAPPED" \
        "success" \
        "Module bootstrap completed successfully."; then

        platform_log_error \
            "Module after-bootstrap event failed: $module"

        return 1
    fi

    platform_module_state_set "$module" "BOOTSTRAPPED" || return 1

    platform_module_hook_dispatch \
        "module.after_bootstrap" \
        "$module" \
        "BOOTSTRAPPED"

    hook_exit_code=$?

    if [[ "$hook_exit_code" -ne 0 ]]; then
        platform_log_error \
            "Module after-bootstrap hook failed: $module"

        return "$hook_exit_code"
    fi

    return 0
}

#
# Executa o bootstrap de todos os módulos resolvidos.
#
# A ordem fornecida pelo Dependency Resolver é preservada.
# Cada módulo publica seus recursos imediatamente antes de seu
# próprio bootstrap.
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