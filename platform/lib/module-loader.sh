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

    source "$module"
  done
}

platform_load_framework_module() {
  local module_dir="$1"
  local manifest="${module_dir}/module.conf"
  local module_name
  local module_enabled
  local module_entrypoint
  local entrypoint

  [[ -f "$manifest" ]] || return 0

  platform_read_module_manifest "$manifest" || return 1

  platform_manifest_registry_register \
    "$MODULE_NAME" \
    "$MODULE_VERSION" \
    "$MODULE_DESCRIPTION" \
    "$MODULE_AUTHOR" \
    "$MODULE_API_VERSION" \
    "$MODULE_ENTRYPOINT" \
    "$MODULE_DEPENDENCIES" \
    "$MODULE_ENABLED" \
    "$manifest" \
    "$module_dir" || return 1

  module_name="$MODULE_NAME"

  module_enabled="$(
    platform_manifest_registry_get "$module_name" enabled
  )" || return 1

  [[ "$module_enabled" == "false" ]] && return 0

  module_entrypoint="$(
    platform_manifest_registry_get "$module_name" entrypoint
  )" || return 1

  entrypoint="${module_dir}/${module_entrypoint}"

  if [[ ! -f "$entrypoint" ]]; then
    platform_log_error "Module entrypoint not found: $entrypoint"
    return 1
  fi

  source "$entrypoint"
}

platform_load_framework_modules() {
  local modules_dir="$1"
  local module_dir

  for module_dir in "$modules_dir"/*; do
    [[ -d "$module_dir" ]] || continue

    platform_load_framework_module "$module_dir" || return 1
  done
}

platform_load_modules() {
  local modules_dir="${PLATFORM_ROOT}/modules"

  [[ -d "$modules_dir" ]] || return 0

  platform_load_legacy_modules "$modules_dir" || return 1
  platform_load_framework_modules "$modules_dir" || return 1
}