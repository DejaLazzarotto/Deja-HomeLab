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

#
# Registra um manifesto no Manifest Registry.
#
platform_register_module_manifest() {
    local module_name="${1:-}"
    local module_version="${2:-}"
    local module_description="${3:-}"
    local module_author="${4:-}"
    local module_api_version="${5:-}"
    local module_entrypoint="${6:-}"
    local module_dependencies="${7:-}"
    local module_enabled="${8:-}"
    local manifest_file="${9:-}"
    local module_dir="${10:-}"

    platform_manifest_registry_register \
        "$module_name" \
        "$module_version" \
        "$module_description" \
        "$module_author" \
        "$module_api_version" \
        "$module_entrypoint" \
        "$module_dependencies" \
        "$module_enabled" \
        "$manifest_file" \
        "$module_dir"
}

#
# Informa se um manifesto já está registrado.
#
platform_is_module_manifest_registered() {
    platform_manifest_registry_has "${1:-}"
}

#
# Retorna o diretório físico de um módulo registrado.
#
platform_get_module_directory() {
    local module="${1:-}"

    if [[ -z "$module" ]]; then
        platform_log_error "Module name not informed."
        return 1
    fi

    platform_manifest_registry_get "$module" module_dir
}