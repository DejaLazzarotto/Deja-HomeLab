#!/usr/bin/env bash

# ==========================================================
# Deja Platform
# Dependency API
# Public Kernel API
# ==========================================================

#
# Retorna a lista de dependências declaradas por um módulo.
#
# Saída:
#   uma dependência por linha
#
platform_get_module_dependencies_list() {
    local module="${1:-}"
    local dependencies
    local dependency

    if [[ -z "$module" ]]; then
        platform_log_error "Module name not informed."
        return 1
    fi

    dependencies="$(platform_get_module_dependencies "$module")" || return 1

    dependencies="${dependencies#"${dependencies%%[![:space:]]*}"}"
    dependencies="${dependencies%"${dependencies##*[![:space:]]}"}"

    [[ -z "$dependencies" ]] && return 0

    for dependency in $dependencies; do
        printf '%s\n' "$dependency"
    done
}

#
# Informa se o módulo possui dependências declaradas.
#
# Retornos:
#   0 = possui dependências
#   1 = não possui dependências ou ocorreu erro
#
platform_module_has_dependencies() {
    local module="${1:-}"
    local dependencies

    if [[ -z "$module" ]]; then
        platform_log_error "Module name not informed."
        return 1
    fi

    dependencies="$(platform_get_module_dependencies_list "$module")" || return 1

    [[ -n "$dependencies" ]]
}

#
# Valida se todas as dependências declaradas estão registradas.
#
platform_validate_module_dependencies() {
    local module="${1:-}"
    local dependencies
    local dependency

    if [[ -z "$module" ]]; then
        platform_log_error "Module name not informed."
        return 1
    fi

    dependencies="$(platform_get_module_dependencies_list "$module")" || return 1

    [[ -z "$dependencies" ]] && return 0

    while IFS= read -r dependency; do
        [[ -z "$dependency" ]] && continue

        if ! platform_list_registered_manifests |
            grep -Fxq -- "$dependency"; then

            platform_log_error \
                "Module dependency is not registered: ${module} -> ${dependency}"

            return 1
        fi
    done <<< "$dependencies"

    return 0
}