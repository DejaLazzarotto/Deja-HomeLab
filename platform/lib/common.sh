#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLATFORM_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

CONFIG_FILE="$PLATFORM_ROOT/config/deja-platform.conf"

# Bibliotecas
source "$PLATFORM_ROOT/lib/log.sh"
source "$PLATFORM_ROOT/lib/validator.sh"

source "$PLATFORM_ROOT/lib/module-registry.sh"
source "$PLATFORM_ROOT/lib/module-loader.sh"

# Configuração
if [[ -f "$CONFIG_FILE" ]]; then
    source "$CONFIG_FILE"
else
    platform_log_error "Configuration file not found:"
    platform_log_error "$CONFIG_FILE"
    exit 1
fi

# Módulos
platform_load_modules