#!/usr/bin/env bash

platform_set_metadata() {
    local key="$1"
    local value="$2"

    platform_context_set_value "metadata" "$key" "$value"
}

platform_get_metadata() {
    local key="$1"

    platform_context_get_value "metadata" "$key"
}

platform_has_metadata() {
    local key="$1"

    platform_context_has_value "metadata" "$key"
}