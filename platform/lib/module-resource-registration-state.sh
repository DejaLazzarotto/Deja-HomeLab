#!/usr/bin/env bash

#
# ==========================================================
# Deja Platform
# Module Resource Registration State
# Internal Kernel Implementation
# ==========================================================
#

#
# Módulos que concluíram com sucesso o estágio oficial de
# Resource Registration.
#
# Este controle é deliberadamente separado do Module State
# Registry para preservar o contrato público de estados:
#
#   DISCOVERED
#   VALIDATED
#   RESOLVED
#   LOADED
#   BOOTSTRAPPED
#
declare -gA PLATFORM_MODULE_RESOURCE_REGISTRATION_STATES=()

#
# Limpa completamente o controle interno de Resource
# Registration.
#
platform_module_resource_registration_state_reset() {
    PLATFORM_MODULE_RESOURCE_REGISTRATION_STATES=()
}

#
# Marca o Resource Registration de um módulo como concluído.
#
# Argumentos:
#
#   $1 - Nome do módulo.
#
platform_module_resource_registration_state_mark_completed() {
    local module="${1:-}"

    [[ -z "$module" ]] && return 1

    PLATFORM_MODULE_RESOURCE_REGISTRATION_STATES["$module"]="completed"
}

#
# Verifica se o módulo já concluiu o Resource Registration.
#
# Argumentos:
#
#   $1 - Nome do módulo.
#
platform_module_resource_registration_state_is_completed() {
    local module="${1:-}"

    [[ -z "$module" ]] && return 1

    [[
        "${PLATFORM_MODULE_RESOURCE_REGISTRATION_STATES[$module]:-}" \
            == "completed"
    ]]
}

#
# Lista os módulos que já concluíram o Resource Registration.
#
platform_module_resource_registration_state_list() {
    printf '%s\n' \
        "${!PLATFORM_MODULE_RESOURCE_REGISTRATION_STATES[@]}"
}