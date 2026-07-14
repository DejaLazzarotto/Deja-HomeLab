#!/usr/bin/env bash

# ==========================================================
# Deja Platform
# Dependency API
# Public Kernel API
# ==========================================================

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

platform_validate_module_dependencies() {
    local module="${1:-}"
    local dependencies
    local dependency

    if [[ -z "$module" ]]; then
        platform_log_error "Module name not informed."
        return 1
    fi

    dependencies="$(platform_get_module_dependencies_list "$module")" || return 1

    if [[ -n "$dependencies" ]]; then
        while IFS= read -r dependency; do
            [[ -z "$dependency" ]] && continue

            if ! platform_list_registered_manifests |
                grep -Fxq -- "$dependency"; then

                platform_log_error \
                    "Module dependency is not registered: ${module} -> ${dependency}"

                return 1
            fi
        done <<< "$dependencies"
    fi

    #
    # Dependências validadas com sucesso.
    #
    platform_module_state_set "$module" "VALIDATED"

    return 0
}

platform_resolve_dependencies() {
    platform_dependency_resolver_run
}

platform_list_resolved_modules() {
    platform_dependency_resolver_list
}

platform_is_module_resolved() {
    local module="${1:-}"
    local resolved_module

    if [[ -z "$module" ]]; then
        platform_log_error "Module name not informed."
        return 1
    fi

    while IFS= read -r resolved_module; do
        [[ "$resolved_module" == "$module" ]] && return 0
    done < <(platform_list_resolved_modules)

    return 1
}