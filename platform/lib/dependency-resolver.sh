#!/usr/bin/env bash

# ==========================================
# DEJA PLATFORM — DEPENDENCY RESOLVER
# ==========================================
#
# Responsável por calcular a ordem de
# inicialização dos módulos com base em suas
# dependências declaradas.
#
# Esta biblioteca apenas resolve a ordem.
# Nenhum módulo é carregado automaticamente.
# ==========================================

declare -ag PLATFORM_RESOLVED_MODULES=()
declare -Ag PLATFORM_RESOLVED_MODULE_INDEX=()

# Verifica se um módulo já existe na lista resolvida.
#
# Uso:
#   platform_module_dependency_exists "core"
#
# Retornos:
#   0 - módulo já presente
#   1 - módulo ainda não presente
platform_module_dependency_exists() {
    local module_name="${1:-}"

    if [[ -z "$module_name" ]]; then
        platform_log_error "Module name not informed."
        return 1
    fi

    [[ -n "${PLATFORM_RESOLVED_MODULE_INDEX[$module_name]:-}" ]]
}

# Limpa o estado interno do Resolver.
platform_dependency_resolver_reset() {
    PLATFORM_RESOLVED_MODULES=()
    PLATFORM_RESOLVED_MODULE_INDEX=()
}

# Adiciona um módulo à lista resolvida sem duplicação.
platform_dependency_resolver_add() {
    local module_name="${1:-}"

    if [[ -z "$module_name" ]]; then
        platform_log_error "Module name not informed."
        return 1
    fi

    if platform_module_dependency_exists "$module_name"; then
        return 0
    fi

    PLATFORM_RESOLVED_MODULES+=("$module_name")
    PLATFORM_RESOLVED_MODULE_INDEX["$module_name"]=1
}

# Resolve recursivamente as dependências de um módulo.
#
# Função interna.
platform_dependency_resolve_recursive() {
    local module_name="${1:-}"
    local dependency=""

    if [[ -z "$module_name" ]]; then
        platform_log_error "Module name not informed."
        return 1
    fi

    if platform_module_dependency_exists "$module_name"; then
        return 0
    fi

    if ! platform_validate_module_dependencies "$module_name"; then
        return 1
    fi

    while IFS= read -r dependency; do
        [[ -z "$dependency" ]] && continue

        if ! platform_dependency_resolve_recursive "$dependency"; then
            return 1
        fi
    done < <(
        platform_get_module_dependencies_list "$module_name" | LC_ALL=C sort
    )

    platform_dependency_resolver_add "$module_name"
}

# Resolve as dependências de um módulo e imprime a ordem calculada.
#
# Uso:
#   platform_resolve_module_dependencies "application"
#
# Exemplo de saída:
#   core
#   database
#   application
platform_resolve_module_dependencies() {
    local module_name="${1:-}"
    local resolved_module=""

    if [[ -z "$module_name" ]]; then
        platform_log_error "Module name not informed."
        return 1
    fi

    platform_dependency_resolver_reset

    if ! platform_dependency_resolve_recursive "$module_name"; then
        return 1
    fi

    for resolved_module in "${PLATFORM_RESOLVED_MODULES[@]}"; do
        printf '%s\n' "$resolved_module"
    done
}

# Resolve todos os módulos informados e imprime uma única ordem,
# eliminando módulos duplicados.
#
# Uso:
#   platform_resolve_all_modules core database application
platform_resolve_all_modules() {
    local module_name=""
    local resolved_module=""

    if [[ "$#" -eq 0 ]]; then
        platform_log_error "No modules informed for dependency resolution."
        return 1
    fi

    platform_dependency_resolver_reset

    while IFS= read -r module_name; do
        [[ -z "$module_name" ]] && continue

        if ! platform_dependency_resolve_recursive "$module_name"; then
            return 1
        fi
    done < <(printf '%s\n' "$@" | LC_ALL=C sort -u)

    for resolved_module in "${PLATFORM_RESOLVED_MODULES[@]}"; do
        printf '%s\n' "$resolved_module"
    done
}
