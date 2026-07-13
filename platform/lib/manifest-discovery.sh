#!/usr/bin/env bash

# ==========================================================
# Deja Platform
# Manifest Discovery
# ==========================================================

platform_manifest_exists_on_disk() {
  local module_dir="${1:-}"

  if [[ -z "$module_dir" ]]; then
    platform_log_error "Module directory is required"
    return 1
  fi

  [[ -f "$module_dir/module.conf" ]]
}

platform_discover_manifest() {
  local module_dir="${1:-}"
  local manifest_file

  if [[ -z "$module_dir" ]]; then
    platform_log_error "Module directory is required"
    return 1
  fi

  if ! platform_manifest_exists_on_disk "$module_dir"; then
    platform_log_error "Module manifest not found: $module_dir/module.conf"
    return 1
  fi

  manifest_file="$module_dir/module.conf"

  platform_read_module_manifest "$manifest_file" || return 1

  platform_register_module_manifest \
    "$MODULE_NAME" \
    "$MODULE_VERSION" \
    "${MODULE_DESCRIPTION:-}" \
    "${MODULE_AUTHOR:-}" \
    "$MODULE_API_VERSION" \
    "$MODULE_ENTRYPOINT" \
    "${MODULE_DEPENDENCIES:-}" \
    "$MODULE_ENABLED" \
    "$manifest_file" \
    "$module_dir"
}

platform_discover_manifests() {
  local modules_dir="${PLATFORM_ROOT}/modules"
  local module_dir

  [[ -d "$modules_dir" ]] || return 0

  for module_dir in "$modules_dir"/*; do
    [[ -d "$module_dir" ]] || continue
    [[ -f "$module_dir/module.conf" ]] || continue

    platform_discover_manifest "$module_dir" || return 1
  done
}