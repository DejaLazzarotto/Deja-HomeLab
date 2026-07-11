#!/usr/bin/env bash

declare -gA PLATFORM_MANIFEST_REGISTRY=()
declare -ga PLATFORM_MANIFEST_REGISTRY_ORDER=()

platform_manifest_registry_key() {
  local module_name="${1:-}"
  local field="${2:-}"

  printf '%s:%s' "$module_name" "$field"
}

platform_manifest_registry_has() {
  local module_name="${1:-}"
  local key

  if [[ -z "$module_name" ]]; then
    platform_log_error "Module name is required"
    return 1
  fi

  key="$(platform_manifest_registry_key "$module_name" "name")"

  [[ -n "${PLATFORM_MANIFEST_REGISTRY[$key]+x}" ]]
}

platform_manifest_registry_register() {
  local module_name="${1:-}"
  local module_version="${2:-}"
  local module_description="${3:-}"
  local module_author="${4:-}"
  local module_api_version="${5:-}"
  local module_entrypoint="${6:-}"
  local module_dependencies="${7:-}"
  local module_enabled="${8:-}"
  local manifest_file="${9:-}"
  local module_dir="${10:-}"

  if [[ -z "$module_name" ]]; then
    platform_log_error "Module name is required"
    return 1
  fi

  if platform_manifest_registry_has "$module_name"; then
    platform_log_error "Module manifest already registered: $module_name"
    return 1
  fi

  PLATFORM_MANIFEST_REGISTRY["${module_name}:name"]="$module_name"
  PLATFORM_MANIFEST_REGISTRY["${module_name}:version"]="$module_version"
  PLATFORM_MANIFEST_REGISTRY["${module_name}:description"]="$module_description"
  PLATFORM_MANIFEST_REGISTRY["${module_name}:author"]="$module_author"
  PLATFORM_MANIFEST_REGISTRY["${module_name}:api_version"]="$module_api_version"
  PLATFORM_MANIFEST_REGISTRY["${module_name}:entrypoint"]="$module_entrypoint"
  PLATFORM_MANIFEST_REGISTRY["${module_name}:dependencies"]="$module_dependencies"
  PLATFORM_MANIFEST_REGISTRY["${module_name}:enabled"]="$module_enabled"
  PLATFORM_MANIFEST_REGISTRY["${module_name}:manifest_file"]="$manifest_file"
  PLATFORM_MANIFEST_REGISTRY["${module_name}:module_dir"]="$module_dir"

  PLATFORM_MANIFEST_REGISTRY_ORDER+=("$module_name")
}

platform_manifest_registry_get() {
  local module_name="${1:-}"
  local field="${2:-}"
  local key

  if [[ -z "$module_name" ]]; then
    platform_log_error "Module name is required"
    return 1
  fi

  if [[ -z "$field" ]]; then
    platform_log_error "Manifest field is required"
    return 1
  fi

  if ! platform_manifest_registry_has "$module_name"; then
    platform_log_error "Module manifest is not registered: $module_name"
    return 1
  fi

  key="$(platform_manifest_registry_key "$module_name" "$field")"

  if [[ -z "${PLATFORM_MANIFEST_REGISTRY[$key]+x}" ]]; then
    platform_log_error "Unknown module manifest field: $field"
    return 1
  fi

  printf '%s\n' "${PLATFORM_MANIFEST_REGISTRY[$key]}"
}

platform_manifest_registry_list() {
  local module_name

  for module_name in "${PLATFORM_MANIFEST_REGISTRY_ORDER[@]}"; do
    printf '%s\n' "$module_name"
  done
}

platform_manifest_registry_clear() {
  PLATFORM_MANIFEST_REGISTRY=()
  PLATFORM_MANIFEST_REGISTRY_ORDER=()
}