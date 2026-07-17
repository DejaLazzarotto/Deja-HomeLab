#!/usr/bin/env bash

platform_register_module "core"

#
# Observa eventos de configuração recebidos pelo módulo core.
#
# O callback é deliberadamente silencioso nesta fase para não
# alterar a saída pública da plataforma.
#
# Argumentos:
#
#   $1 - Contexto estruturado do Module Event Dispatcher.
#
platform_module_core_configuration_observer() {
    local context="${1:-}"
    local event
    local module
    local status

    [[ -z "$context" ]] && return 1

    event="$(
        platform_module_event_context_get \
            "$context" \
            "event"
    )" || return 1

    module="$(
        platform_module_event_context_get \
            "$context" \
            "module"
    )" || return 1

    status="$(
        platform_module_event_context_get \
            "$context" \
            "status"
    )" || return 1

    [[ -z "$event" ]] && return 1
    [[ -z "$module" ]] && return 1
    [[ -z "$status" ]] && return 1

    return 0
}

#
# Publica os Commands pertencentes ao módulo core.
#
platform_module_core_register_commands() {
    platform_register_module_command \
        "core" \
        "core:status" \
        "$PLATFORM_ROOT/modules/core/commands/status.sh" \
        "platform_cmd_core_status" \
        "Show core module status"
}

#
# Publica os Configuration Providers internos do Kernel.
#
# Esta função mantém o conhecimento sobre os providers builtin
# encapsulado em sua API específica. O módulo core apenas define
# o momento oficial em que esses recursos são publicados.
#
platform_module_core_register_configuration_providers() {
    platform_register_builtin_module_config_providers
}

#
# Publica os Configuration Observers pertencentes ao módulo core.
#
platform_module_core_register_configuration_observers() {
    platform_module_config_observer_register \
        "core" \
        "core.configuration" \
        "platform_module_core_configuration_observer"
}

#
# Publica os recursos do módulo core durante seu estágio oficial
# de Resource Registration.
#
# Cada categoria de recurso possui uma função dedicada. Esse
# padrão poderá ser reutilizado nas próximas migrações sem
# concentrar todos os registros diretamente neste contrato.
#
platform_module_core_register_resources() {
    platform_module_core_register_commands \
        || return 1

    platform_module_core_register_configuration_providers \
        || return 1

    platform_module_core_register_configuration_observers \
        || return 1
}