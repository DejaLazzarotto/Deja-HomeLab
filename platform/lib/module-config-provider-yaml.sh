#!/usr/bin/env bash

#
# ==========================================================
# Deja Platform
# YAML Module Configuration Provider
# Internal Kernel Implementation
# ==========================================================
#

#
# Retorna o caminho padrão do arquivo YAML de configuração
# pertencente a um módulo.
#
# Argumentos:
#
#   $1 - Nome do módulo.
#
platform_module_config_provider_yaml_get_file() {
    local module="${1:-}"

    if [[ -z "$module" ]]; then
        return 1
    fi

    printf '%s\n' \
        "$PLATFORM_ROOT/modules/$module/config.yaml"
}

#
# Garante que a configuração YAML de um módulo esteja
# carregada no cache interno.
#
# O carregamento é idempotente. Após a primeira tentativa,
# o arquivo não será lido novamente durante o mesmo ciclo
# de execução do Kernel.
#
# Argumentos:
#
#   $1 - Nome do módulo.
#
platform_module_config_provider_yaml_ensure_loaded() {
    local module="${1:-}"
    local config_file

    if [[ -z "$module" ]]; then
        platform_log_error \
            "Module name not informed for YAML configuration loading."
        return 1
    fi

    if platform_module_config_yaml_cache_is_loaded "$module"; then
        return 0
    fi

    config_file="$(
        platform_module_config_provider_yaml_get_file "$module"
    )" || return 1

    platform_module_config_yaml_cache_load \
        "$module" \
        "$config_file"
}

#
# Resolve uma configuração simples através do cache YAML
# interno do módulo.
#
# O arquivo YAML será carregado somente na primeira consulta
# realizada durante o ciclo atual de execução do Kernel.
#
# Formato suportado nesta fase:
#
#   chave: valor
#
# Não são suportados:
#
#   - objetos aninhados;
#   - arrays;
#   - múltiplos documentos;
#   - anchors ou aliases;
#   - blocos multilinha;
#   - chaves duplicadas;
#   - merge de arquivos.
#
# Argumentos:
#
#   $1 - Nome do módulo.
#   $2 - Chave da configuração.
#
# Retorno:
#
#   0 - Configuração encontrada.
#   1 - Arquivo ou configuração não encontrados.
#
platform_module_config_provider_yaml_resolve() {
    local module="${1:-}"
    local key="${2:-}"

    if [[ -z "$module" ]]; then
        platform_log_error \
            "Module name not informed for YAML configuration resolution."
        return 1
    fi

    if [[ -z "$key" ]]; then
        platform_log_error \
            "Configuration key not informed for YAML provider: module=$module"
        return 1
    fi

    platform_module_config_provider_yaml_ensure_loaded "$module" || return 1

    platform_module_config_yaml_cache_get \
        "$module" \
        "$key"
}