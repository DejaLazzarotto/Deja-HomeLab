#!/usr/bin/env bash

platform_register_service() {
    local service_name="$1"
    local service_provider="$2"

    platform_context_set_value "services" "$service_name" "$service_provider"
}

platform_get_service() {
    local service_name="$1"

    platform_context_get_value "services" "$service_name"
}

platform_has_service() {
    local service_name="$1"

    platform_context_has_value "services" "$service_name"
}