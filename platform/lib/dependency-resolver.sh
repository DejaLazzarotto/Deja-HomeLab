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
declare -gA PLATFORM_DEPENDENCY_PROCESSING=()
declare -ga PLATFORM_DEPENDENCY_STACK=()

#
# Limpa o estado interno do Dependency Resolver.
#
platform_dependency_resolver_reset() {
    PLATFORM_RESOLVED_MODULES=()
    PLATFORM_DEPENDENCY_VISITED=()
    PLATFORM_DEPENDENCY_PROCESSING=()
    PLATFORM_DEPENDENCY_STACK=()
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
# Marca um módulo como completamente visitado.
#
platform_dependency_resolver_mark_visited() {
    local module="$1"

    [[ -z "$module" ]] && return 1

    PLATFORM_DEPENDENCY_VISITED["$module"]=1
}

#
# Verifica se um módulo já foi completamente visitado.
#
platform_dependency_resolver_is_visited() {
    local module="$1"

    [[ -z "$module" ]] && return 1
    [[ -n "${PLATFORM_DEPENDENCY_VISITED[$module]:-}" ]]
}

#
# Marca um módulo como estando em processamento.
#
platform_dependency_resolver_mark_processing() {
    local module="$1"

    [[ -z "$module" ]] && return 1

    PLATFORM_DEPENDENCY_PROCESSING["$module"]=1
    PLATFORM_DEPENDENCY_STACK+=("$module")
}

#
# Remove um módulo do estado de processamento.
#
platform_dependency_resolver_unmark_processing() {
    local module="$1"
    local stack_size

    [[ -z "$module" ]] && return 1

    unset 'PLATFORM_DEPENDENCY_PROCESSING[$module]'

    stack_size="${#PLATFORM_DEPENDENCY_STACK[@]}"

    if (( stack_size > 0 )); then
        unset 'PLATFORM_DEPENDENCY_STACK[stack_size - 1]'
        PLATFORM_DEPENDENCY_STACK=("${PLATFORM_DEPENDENCY_STACK[@]}")
    fi
}

#
# Verifica se um módulo está atualmente em processamento.
#
platform_dependency_resolver_is_processing() {
    local module="$1"

    [[ -z "$module" ]] && return 1
    [[ -n "${PLATFORM_DEPENDENCY_PROCESSING[$module]:-}" ]]
}

#
# Monta uma representação textual do ciclo encontrado.
#
platform_dependency_resolver_format_cycle() {
    local repeated_module="$1"
    local current_module
    local cycle=""
    local cycle_started=false

    [[ -z "$repeated_module" ]] && return 1

    for current_module in "${PLATFORM_DEPENDENCY_STACK[@]}"; do
        if [[ "$current_module" == "$repeated_module" ]]; then
            cycle_started=true
        fi

        if [[ "$cycle_started" == true ]]; then
            if [[ -n "$cycle" ]]; then
                cycle+=" -> "
            fi

            cycle+="$current_module"
        fi
    done

    if [[ -n "$cycle" ]]; then
        cycle+=" -> $repeated_module"
    else
        cycle="$repeated_module -> $repeated_module"
    fi

    printf '%s\n' "$cycle"
}

#
# Informa a detecção de uma dependência circular.
#
platform_dependency_resolver_report_cycle() {
    local module="$1"
    local cycle

    [[ -z "$module" ]] && return 1

    cycle="$(platform_dependency_resolver_format_cycle "$module")"

    platform_log_error "Circular module dependency detected: $cycle"
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

    if platform_dependency_resolver_is_processing "$module"; then
        platform_dependency_resolver_report_cycle "$module"
        return 1
    fi

    platform_dependency_resolver_is_visited "$module" && return 0

    platform_dependency_resolver_mark_processing "$module" || return 1

    dependencies="$(platform_get_module_dependencies "$module")" || {
        platform_dependency_resolver_unmark_processing "$module"
        return 1
    }

    for dependency in $dependencies; do
        [[ -z "$dependency" ]] && continue

        if ! platform_dependency_resolver_visit "$dependency"; then
            platform_dependency_resolver_unmark_processing "$module"
            return 1
        fi
    done

    platform_dependency_resolver_unmark_processing "$module" || return 1
    platform_dependency_resolver_mark_visited "$module" || return 1
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