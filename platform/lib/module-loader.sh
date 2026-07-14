#!/usr/bin/env bash

platform_load_legacy_modules() {
  local modules_dir="$1"
  local module
  local module_name

  for module in "$modules_dir"/*.module.sh; do
    [[ -f "$module" ]] || continue

    module_name="$(basename "$module" .module.sh)"

    if [[ -f "$modules_dir/$module_name/module.conf" ]]; then
      continue
    fi

    source "$module" || return 1
  done
}

platform_load_framework_module() {
  local module_name="${1:-}"
  local module_dir
  local module_entrypoint
  local entrypoint

  if [[ -z "$module_name" ]]; then
    platform_log_error "Module name is required"
    return 1
  fi

  platform_is_module_resolved "$module_name" || {
    platform_log_error "Module is not resolved: $module_name"
    return 1
  }

  platform_is_module_manifest_registered "$module_name" || {
    platform_log_error "Module manifest is not registered: $module_name"
    return 1
  }

  platform_is_module_enabled "$module_name" || return 0

  module_dir="$(
    platform_get_module_directory "$module_name"
  )" || return 1

  module_entrypoint="$(
    platform_get_module_entrypoint "$module_name"
  )" || return 1

  entrypoint="${module_dir}/${module_entrypoint}"

  if [[ ! -f "$entrypoint" ]]; then
    platform_log_error "Module entrypoint not found: $entrypoint"
    return 1
  fi

  source "$entrypoint" || return 1

  platform_module_state_set "$module_name" "LOADED"
}

platform_load_framework_modules() {
  local module_name

  while IFS= read -r module_name; do
    [[ -n "$module_name" ]] || continue

    platform_load_framework_module "$module_name" || return 1
  done < <(platform_list_resolved_modules)
}

platform_load_modules() {
  local modules_dir="${PLATFORM_ROOT}/modules"

  [[ -d "$modules_dir" ]] || return 0

  #
  # Compatibilidade temporária com módulos legados.
  # Será removida quando toda a plataforma utilizar manifests.
  #
  platform_load_legacy_modules "$modules_dir" || return 1

  #
  # Framework Modules
  #
  platform_load_framework_modules || return 1
}