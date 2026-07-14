#!/usr/bin/env bash

#
# ==========================================================
# Deja Platform
# Dependency Resolver
# Internal Kernel Implementation
# ==========================================================
#

declare -ga PLATFORM_RESOLVED_MODULES=()
declare -gA PLATFORM_DEPENDENCY_VISITED=()

#
# Limpa o estado interno do Dependency Resolver.
#
platform_dependency_resolver_reset() {
    PLATFORM_RESOLVED_MODULES=()
    PLATFORM_DEPENDENCY_VISITED=()
}

#
# Adiciona um módulo à lista oficial de módulos resolvidos.
#
# O módulo não será adicionado novamente caso já esteja presente.
#
platform_dependency_resolver_add() {
    local module="$1"
    local existing

    [[ -z "$module" ]] && return 1

    for existing in "${PLATFORM_RESOLVED_MODULES[@]}"; do
        [[ "$existing" == "$module" ]] && return 0
    done

    PLATFORM_RESOLVED_MODULES+=("$module")
}

#
# Marca um módulo como visitado durante a travessia do grafo.
#
platform_dependency_resolver_mark_visited() {
    local module="$1"

    [[ -z "$module" ]] && return 1

    PLATFORM_DEPENDENCY_VISITED["$module"]=1
}

#
# Verifica se um módulo já foi visitado.
#
platform_dependency_resolver_is_visited() {
    local module="$1"

    [[ -z "$module" ]] && return 1
    [[ -n "${PLATFORM_DEPENDENCY_VISITED[$module]:-}" ]]
}

#
# Resolve um módulo utilizando busca em profundidade.
#
# Todas as dependências são visitadas antes que o próprio módulo
# seja incluído na lista final de carregamento.
#
platform_dependency_resolver_visit() {
    local module="$1"
    local dependencies
    local dependency

    [[ -z "$module" ]] && return 1

    platform_dependency_resolver_is_visited "$module" && return 0

    platform_dependency_resolver_mark_visited "$module"

    dependencies="$(platform_get_module_dependencies "$module")" || return 1

    for dependency in $dependencies; do
        [[ -z "$dependency" ]] && continue

        platform_dependency_resolver_visit "$dependency" || return 1
    done

    platform_dependency_resolver_add "$module"
}

#
# Executa a resolução topológica de todos os módulos registrados.
#
# A ordem final não depende da ordem em que os manifests foram
# descobertos. Cada módulo é inserido somente depois de todas
# as suas dependências.
#
platform_dependency_resolver_run() {
    local module

    platform_dependency_resolver_reset

    while IFS= read -r module; do
        [[ -z "$module" ]] && continue

        platform_dependency_resolver_visit "$module" || return 1
    done < <(platform_list_registered_manifests)

    return 0
}

#
# Lista os módulos na ordem final calculada pelo Resolver.
#
platform_dependency_resolver_list() {
    printf '%s\n' "${PLATFORM_RESOLVED_MODULES[@]}"
}