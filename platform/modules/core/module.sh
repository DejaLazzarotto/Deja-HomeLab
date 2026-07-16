#!/usr/bin/env bash

platform_register_module "core"

platform_register_module_command \
  "core" \
  "core:status" \
  "$PLATFORM_ROOT/modules/core/commands/status.sh" \
  "platform_cmd_core_status" \
  "Show core module status"

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
# Publica os recursos do módulo core durante seu estágio oficial
# de Resource Registration.
#
platform_module_core_register_resources() {
    platform_module_config_observer_register \
        "core" \
        "core.configuration" \
        "platform_module_core_configuration_observer"
}