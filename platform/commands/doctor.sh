#!/usr/bin/env bash

platform_cmd_doctor() {
  platform_log_info "Running Deja Platform environment checks"
  echo ""

  local has_error=0

  platform_log_info "Checking required commands..."
  platform_require_command "bash" || has_error=1
  platform_require_command "git" || has_error=1

  echo ""
  platform_log_info "Checking platform structure..."
  platform_require_directory "$PLATFORM_ROOT/bin" || has_error=1
  platform_require_directory "$PLATFORM_ROOT/commands" || has_error=1
  platform_require_directory "$PLATFORM_ROOT/config" || has_error=1
  platform_require_directory "$PLATFORM_ROOT/lib" || has_error=1

  echo ""
  platform_log_info "Checking core files..."
  platform_require_readable_file "$PLATFORM_ROOT/config/deja-platform.conf" || has_error=1
  platform_require_readable_file "$PLATFORM_ROOT/lib/common.sh" || has_error=1
  platform_require_readable_file "$PLATFORM_ROOT/lib/log.sh" || has_error=1
  platform_require_readable_file "$PLATFORM_ROOT/lib/parser.sh" || has_error=1
  platform_require_readable_file "$PLATFORM_ROOT/lib/validator.sh" || has_error=1

  echo ""
  if [[ "$has_error" -eq 0 ]]; then
    platform_log_success "Environment checks completed successfully"
    return 0
  fi

  platform_log_error "Environment checks failed"
  return 1
}