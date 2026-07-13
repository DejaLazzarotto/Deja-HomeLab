#!/usr/bin/env bash

# ==========================================================
# Deja Platform
# Dependency Resolver
# Internal Kernel Implementation
# ==========================================================

declare -ga PLATFORM_RESOLVED_MODULES=()

platform_dependency_resolver_reset() {
    PLATFORM_RESOLVED_MODULES=()
}

platform_dependency_resolver_add() {
    local module="${1:-}"
    local existing

    if [[ -z "$module" ]]; then
        platform_log_error "Module name not informed."
        return 1
    fi

    for existing in "${PLATFORM_RESOLVED_MODULES[@]}"; do
        [[ "$existing" == "$module" ]] && return 0
    done

    PLATFORM_RESOLVED_MODULES+=("$module")
}

platform_dependency_resolver_list() {
    local module

    for module in "${PLATFORM_RESOLVED_MODULES[@]}"; do
        printf '%s\n' "$module"
    done
}

platform_dependency_resolver_run() {
    local module
    local dependency

    platform_dependency_resolver_reset

    while IFS= read -r module; do
        [[ -z "$module" ]] && continue

        platform_validate_module_dependencies "$module" || {
            platform_dependency_resolver_reset
            return 1
        }

        while IFS= read -r dependency; do
            [[ -z "$dependency" ]] && continue

            platform_dependency_resolver_add "$dependency" || {
                platform_dependency_resolver_reset
                return 1
            }
        done < <(platform_get_module_dependencies_list "$module")

        platform_dependency_resolver_add "$module" || {
            platform_dependency_resolver_reset
            return 1
        }
    done < <(platform_list_registered_manifests)

    return 0
}
