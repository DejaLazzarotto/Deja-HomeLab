#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLATFORM_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

CONFIG_FILE="$PLATFORM_ROOT/config/deja-platform.conf"

# Bibliotecas
source "$PLATFORM_ROOT/lib/log.sh"
source "$PLATFORM_ROOT/lib/validator.sh"

# Kernel
source "$PLATFORM_ROOT/lib/context.sh"
source "$PLATFORM_ROOT/lib/context-api.sh"
source "$PLATFORM_ROOT/lib/service-api.sh"
source "$PLATFORM_ROOT/lib/runtime-api.sh"
source "$PLATFORM_ROOT/lib/metadata-api.sh"

# Command System
source "$PLATFORM_ROOT/lib/command-registry.sh"
source "$PLATFORM_ROOT/lib/command-loader.sh"

# Module System
source "$PLATFORM_ROOT/lib/module-registry.sh"
source "$PLATFORM_ROOT/lib/module-api.sh"
source "$PLATFORM_ROOT/lib/manifest-loader.sh"
source "$PLATFORM_ROOT/lib/manifest-registry.sh"
source "$PLATFORM_ROOT/lib/manifest-api.sh"
source "$PLATFORM_ROOT/lib/manifest-discovery.sh"
source "$PLATFORM_ROOT/lib/dependency-api.sh"
source "$PLATFORM_ROOT/lib/dependency-resolver.sh"
source "$PLATFORM_ROOT/lib/module-state.sh"
source "$PLATFORM_ROOT/lib/module-loader.sh"
source "$PLATFORM_ROOT/lib/module-lifecycle.sh"
source "$PLATFORM_ROOT/lib/module-event-registry.sh"
source "$PLATFORM_ROOT/lib/module-event-dispatcher.sh"
source "$PLATFORM_ROOT/lib/module-hook-registry.sh"
source "$PLATFORM_ROOT/lib/module-hook-dispatcher.sh"
source "$PLATFORM_ROOT/lib/module-extension-registry.sh"
source "$PLATFORM_ROOT/lib/module-extension-dispatcher.sh"
source "$PLATFORM_ROOT/lib/module-service-registry.sh"
source "$PLATFORM_ROOT/lib/module-service-dispatcher.sh"
source "$PLATFORM_ROOT/lib/module-capability-registry.sh"
source "$PLATFORM_ROOT/lib/module-lifecycle-manager.sh"

# Configuração
if [[ -f "$CONFIG_FILE" ]]; then
    source "$CONFIG_FILE"
else
    platform_log_error "Configuration file not found:"
    platform_log_error "$CONFIG_FILE"
    exit 1
fi

# Inicialização do Kernel
platform_context_init
platform_module_state_reset
platform_module_event_reset
platform_module_event_dispatcher_init
platform_module_extension_registry_reset
platform_module_capability_registry_reset

# Comandos internos
platform_register_builtin_commands

# Descoberta dos manifests
platform_set_module_lifecycle_stage "discover"
platform_discover_manifests || exit 1

# Resolução das dependências
platform_resolve_dependencies || exit 1

# Carregamento dos módulos
platform_set_module_lifecycle_stage "load"
platform_load_modules || exit 1
platform_module_lifecycle_bootstrap_all || return 1

# Bootstrap dos módulos
platform_set_module_lifecycle_stage "bootstrap"
platform_bootstrap_modules