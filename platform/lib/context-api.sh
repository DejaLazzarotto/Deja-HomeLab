#!/usr/bin/env bash

platform_context_register_namespace() {
    platform_context_create_namespace "$1"
}

platform_context_set_value() {
    local namespace="$1"
    local key="$2"
    local value="$3"

    platform_context_set "$namespace" "$key" "$value"
}

platform_context_get_value() {
    local namespace="$1"
    local key="$2"

    platform_context_get "$namespace" "$key"
}

platform_context_has_value() {
    local namespace="$1"
    local key="$2"

    platform_context_has "$namespace" "$key"
}