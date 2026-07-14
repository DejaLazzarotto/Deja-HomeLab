#!/usr/bin/env bash

#
# ==========================================================
# Deja Platform
# Module Service Dispatcher
# Internal Kernel Implementation
# ==========================================================
#

#
# Executa um Service interno registrado.
#
platform_module_service_dispatch() {
    local service="${1:-}"
    local service_function

    if [[ -z "$service" ]]; then
        platform_log_error "Service name not informed."
        return 1
    fi

    if ! platform_module_service_exists "$service"; then
        platform_log_error "Service not registered: $service"
        return 1
    fi

    service_function="$(platform_module_service_get_function "$service")" || return 1

    if [[ -z "$service_function" ]]; then
        platform_log_error "Service implementation not informed: $service"
        return 1
    fi

    if ! declare -F "$service_function" >/dev/null 2>&1; then
        platform_log_error \
            "Service implementation function not found: $service_function"
        return 1
    fi

    shift

    "$service_function" "$@"
}