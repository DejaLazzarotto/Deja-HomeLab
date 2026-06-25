#!/usr/bin/env bash

platform_log_info() {
  echo "[INFO] $*"
}

platform_log_warn() {
  echo "[WARN] $*" >&2
}

platform_log_error() {
  echo "[ERROR] $*" >&2
}

platform_log_success() {
  echo "[OK] $*"
}