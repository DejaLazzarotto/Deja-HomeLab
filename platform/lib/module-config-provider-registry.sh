#!/usr/bin/env bash

#
# ==========================================================
# Deja Platform
# Module Configuration Provider Registry
# Internal Kernel Implementation
# ==========================================================
#

#
# Funções responsáveis pela resolução de configurações,
# indexadas pelo nome do provider.
#
declare -gA PLATFORM_MODULE_CONFIG_PROVIDER_RESOLVERS=()

#
# Ordem oficial de registro dos providers.
#
# A ordem será utilizada futuramente para permitir resolução
# encadeada de configurações através de múltiplos providers.
#
declare -ga PLATFORM_MODULE_CONFIG_PROVIDERS=()

#
# Limpa completamente o registro de providers.
#
platform_module_config_provider_registry_reset() {
    PLATFORM_MODULE_CONFIG_PROVIDER_RESOLVERS=()
    PLATFORM_MODULE_CONFIG_PROVIDERS=()
}

#
# Registra um provider de configuração.
#
# Argumentos:
#
#   $1 - Nome único do provider.
#   $2 - Função responsável pela resolução.
#
platform_module_config_provider_registry_register() {
    local provider="${1:-}"
    local resolver_function="${2:-}"

    if [[ -z "$provider" ]]; then
        platform_log_error "Configuration provider name not informed."
        return 1
    fi

    if [[ -z "$resolver_function" ]]; then
        platform_log_error \
            "Configuration provider resolver function not informed: provider=$provider"
        return 1
    fi

    if ! declare -F "$resolver_function" > /dev/null; then
        platform_log_error \
            "Configuration provider resolver function not found: provider=$provider function=$resolver_function"
        return 1
    fi

    if platform_module_config_provider_registry_has "$provider"; then
        platform_log_error \
            "Configuration provider already registered: provider=$provider"
        return 1
    fi

    PLATFORM_MODULE_CONFIG_PROVIDER_RESOLVERS["$provider"]="$resolver_function"
    PLATFORM_MODULE_CONFIG_PROVIDERS+=("$provider")
}

#
# Verifica se um provider está registrado.
#
platform_module_config_provider_registry_has() {
    local provider="${1:-}"

    [[ -z "$provider" ]] && return 1

    [[ -n "${PLATFORM_MODULE_CONFIG_PROVIDER_RESOLVERS[$provider]+_}" ]]
}

#
# Retorna a função de resolução associada ao provider.
#
platform_module_config_provider_registry_get_resolver() {
    local provider="${1:-}"

    if [[ -z "$provider" ]]; then
        return 1
    fi

    if ! platform_module_config_provider_registry_has "$provider"; then
        return 1
    fi

    printf '%s\n' \
        "${PLATFORM_MODULE_CONFIG_PROVIDER_RESOLVERS[$provider]}"
}

#
# Lista os providers na ordem oficial de registro.
#
platform_module_config_provider_registry_list() {
    local provider

    for provider in "${PLATFORM_MODULE_CONFIG_PROVIDERS[@]}"; do
        printf '%s\n' "$provider"
    done
}

#
# Executa internamente o resolver de um provider.
#
# Os argumentos adicionais são encaminhados diretamente
# para a função de resolução registrada.
#
platform_module_config_provider_registry_resolve() {
    local provider="${1:-}"
    local resolver_function

    if [[ -z "$provider" ]]; then
        platform_log_error "Configuration provider name not informed for resolution."
        return 1
    fi

    resolver_function="$(
        platform_module_config_provider_registry_get_resolver "$provider"
    )" || {
        platform_log_error \
            "Configuration provider not registered: provider=$provider"
        return 1
    }

    shift

    "$resolver_function" "$@"
}