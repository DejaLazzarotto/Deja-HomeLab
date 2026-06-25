#!/usr/bin/env bash

platform_load_modules() {
  local modules_dir="${PLATFORM_ROOT}/modules"

  [[ -d "$modules_dir" ]] || return 0

  local module

  for module in "$modules_dir"/*.module.sh; do
    [[ -f "$module" ]] || continue
    source "$module"
  done
}