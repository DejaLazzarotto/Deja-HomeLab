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
# Remove espaços em branco do início e do final de um valor.
#
# Argumentos:
#
#   $1 - Valor que será normalizado.
#
platform_module_config_provider_yaml_trim() {
    local value="${1-}"

    value="${value#"${value%%[![:space:]]*}"}"
    value="${value%"${value##*[![:space:]]}"}"

    printf '%s\n' "$value"
}

#
# Remove aspas simples ou duplas que envolvam completamente
# um valor YAML simples.
#
# Argumentos:
#
#   $1 - Valor que será normalizado.
#
platform_module_config_provider_yaml_unquote() {
    local value="${1-}"

    if [[ "$value" == \"*\" && "$value" == *\" ]]; then
        value="${value:1:${#value}-2}"
    elif [[ "$value" == \'*\' && "$value" == *\' ]]; then
        value="${value:1:${#value}-2}"
    fi

    printf '%s\n' "$value"
}

#
# Resolve uma configuração simples a partir do arquivo YAML
# padrão de um módulo.
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
    local config_file
    local line
    local yaml_key
    local yaml_value

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

    config_file="$(
        platform_module_config_provider_yaml_get_file "$module"
    )" || return 1

    [[ -f "$config_file" ]] || return 1

    while IFS= read -r line || [[ -n "$line" ]]; do
        line="$(
            platform_module_config_provider_yaml_trim "$line"
        )"

        [[ -z "$line" ]] && continue
        [[ "$line" == \#* ]] && continue
        [[ "$line" != *:* ]] && continue

        yaml_key="${line%%:*}"
        yaml_value="${line#*:}"

        yaml_key="$(
            platform_module_config_provider_yaml_trim "$yaml_key"
        )"

        [[ "$yaml_key" == "$key" ]] || continue

        yaml_value="$(
            platform_module_config_provider_yaml_trim "$yaml_value"
        )"

        yaml_value="$(
            platform_module_config_provider_yaml_unquote "$yaml_value"
        )"

        printf '%s\n' "$yaml_value"
        return 0
    done < "$config_file"

    return 1
}