#!/usr/bin/env bash

#
# ==========================================================
# Deja Platform
# Manifest Public API
# ==========================================================
#

#
# Retorna um campo público do manifesto de um módulo.
#
platform_get_module_manifest_field() {
    local module="${1:-}"
    local field="${2:-}"

    if [[ -z "$module" ]]; then
        platform_log_error "Module name not informed."
        return 1
    fi

    if [[ -z "$field" ]]; then
        platform_log_error "Manifest field not informed."
        return 1
    fi

    case "$field" in
        name|version|description|author|api_version|entrypoint|dependencies|enabled)
            ;;
        *)
            platform_log_error "Unknown public manifest field: $field"
            return 1
            ;;
    esac

    platform_manifest_registry_get "$module" "$field"
}

#
# Retorna a versão do módulo.
#
platform_get_module_version() {
    platform_get_module_manifest_field "${1:-}" version
}

#
# Retorna a versão da API suportada pelo módulo.
#
platform_get_module_api_version() {
    platform_get_module_manifest_field "${1:-}" api_version
}

#
# Retorna o entrypoint do módulo.
#
platform_get_module_entrypoint() {
    platform_get_module_manifest_field "${1:-}" entrypoint
}

#
# Retorna as dependências declaradas pelo módulo.
#
platform_get_module_dependencies() {
    platform_get_module_manifest_field "${1:-}" dependencies
}

#
# Informa se um módulo está habilitado.
#
# Retornos:
#   0 = habilitado
#   1 = desabilitado ou erro
#
platform_is_module_enabled() {
    local module="${1:-}"
    local enabled

    enabled="$(platform_get_module_manifest_field "$module" enabled)" || return 1

    [[ "$enabled" == "true" ]]
}

#
# Lista os nomes dos módulos que possuem manifests registrados.
#
platform_list_registered_manifests() {
    platform_manifest_registry_list
}