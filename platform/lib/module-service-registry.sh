#!/usr/bin/env bash

#
# ==========================================================
# Deja Platform
# Module Service Registry
# Internal Kernel Implementation
# ==========================================================
#

declare -gA PLATFORM_MODULE_SERVICE_MODULES=()
declare -gA PLATFORM_MODULE_SERVICE_FUNCTIONS=()
declare -ga PLATFORM_MODULE_SERVICE_NAMES=()

#
# Limpa completamente o registro de Services.
#
platform_module_service_registry_reset() {
    PLATFORM_MODULE_SERVICE_MODULES=()
    PLATFORM_MODULE_SERVICE_FUNCTIONS=()
    PLATFORM_MODULE_SERVICE_NAMES=()
}

#
# Registra um Service interno.
#
platform_module_service_register() {
    local module="${1:-}"
    local service="${2:-}"
    local function="${3:-}"

    [[ -z "$module" ]] && return 1
    [[ -z "$service" ]] && return 1
    [[ -z "$function" ]] && return 1

    if [[ -n "${PLATFORM_MODULE_SERVICE_FUNCTIONS[$service]:-}" ]]; then
        platform_log_error "Service already registered: $service"
        return 1
    fi

    PLATFORM_MODULE_SERVICE_MODULES["$service"]="$module"
    PLATFORM_MODULE_SERVICE_FUNCTIONS["$service"]="$function"
    PLATFORM_MODULE_SERVICE_NAMES+=("$service")
}

#
# Verifica se um Service está registrado.
#
platform_module_service_exists() {
    local service="${1:-}"

    [[ -z "$service" ]] && return 1

    [[ -n "${PLATFORM_MODULE_SERVICE_FUNCTIONS[$service]:-}" ]]
}

#
# Retorna o módulo proprietário do Service.
#
platform_module_service_get_module() {
    local service="${1:-}"

    [[ -z "$service" ]] && return 1

    printf '%s\n' "${PLATFORM_MODULE_SERVICE_MODULES[$service]}"
}

#
# Retorna a função responsável pelo Service.
#
platform_module_service_get_function() {
    local service="${1:-}"

    [[ -z "$service" ]] && return 1

    printf '%s\n' "${PLATFORM_MODULE_SERVICE_FUNCTIONS[$service]}"
}

#
# Lista todos os Services registrados.
#
platform_module_service_registry_list() {
    printf '%s\n' "${PLATFORM_MODULE_SERVICE_NAMES[@]}"
}