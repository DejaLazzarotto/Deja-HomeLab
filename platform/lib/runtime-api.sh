#!/usr/bin/env bash

platform_set_runtime() {
    local key="$1"
    local value="$2"

    platform_context_set_value "runtime" "$key" "$value"
}

platform_get_runtime() {
    local key="$1"

    platform_context_get_value "runtime" "$key"
}

platform_has_runtime() {
    local key="$1"

    platform_context_has_value "runtime" "$key"
}