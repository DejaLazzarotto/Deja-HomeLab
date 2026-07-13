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
source "$PLATFORM_ROOT/lib/module-loader.sh"
source "$PLATFORM_ROOT/lib/module-lifecycle.sh"

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

# Comandos internos
platform_register_builtin_commands

# Descoberta dos manifests
platform_set_module_lifecycle_stage "discover"
platform_discover_manifests

# Carregamento dos módulos
platform_set_module_lifecycle_stage "load"
platform_load_modules

# Bootstrap dos módulos
platform_set_module_lifecycle_stage "bootstrap"
platform_bootstrap_modules