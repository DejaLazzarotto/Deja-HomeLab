#!/usr/bin/env bash

platform_load_modules() {
  local modules_dir="${PLATFORM_ROOT}/modules"

  [[ -d "$modules_dir" ]] || return 0

  local module

#
# Compatibilidade (v1)
#
for module in "$modules_dir"/*.module.sh; do
  [[ -f "$module" ]] || continue

  local module_name
  module_name="$(basename "$module" .module.sh)"

  if [[ -f "$modules_dir/$module_name/module.conf" ]]; then
    continue
  fi

  source "$module"
done

  #
  # Novo contrato (Framework)
  #
  local module_dir
  local manifest
  local entrypoint

  for module_dir in "$modules_dir"/*; do
    [[ -d "$module_dir" ]] || continue

    manifest="${module_dir}/module.conf"
    [[ -f "$manifest" ]] || continue

    unset \
      MODULE_NAME \
      MODULE_VERSION \
      MODULE_DESCRIPTION \
      MODULE_AUTHOR \
      MODULE_API_VERSION \
      MODULE_ENTRYPOINT \
      MODULE_DEPENDENCIES \
      MODULE_ENABLED

    source "$manifest"

    [[ "${MODULE_ENABLED}" == "false" ]] && continue

    entrypoint="${module_dir}/${MODULE_ENTRYPOINT}"

    [[ -f "$entrypoint" ]] || continue

    source "$entrypoint"
  done
}