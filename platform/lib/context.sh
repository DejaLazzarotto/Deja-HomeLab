#!/usr/bin/env bash

declare -gA PLATFORM_CONTEXT=()

platform_context_init() {
    PLATFORM_CONTEXT=()

    platform_context_create_namespace "services"
    platform_context_create_namespace "runtime"
    platform_context_create_namespace "metadata"
    platform_context_create_namespace "config"
    platform_context_create_namespace "modules"
}

platform_context_create_namespace() {
    local namespace="$1"

    PLATFORM_CONTEXT["${namespace}.__namespace__"]=1
}

platform_context_set() {
    local namespace="$1"
    local key="$2"
    local value="$3"

    PLATFORM_CONTEXT["${namespace}.${key}"]="$value"
}

platform_context_get() {
    local namespace="$1"
    local key="$2"

    printf '%s\n' "${PLATFORM_CONTEXT["${namespace}.${key}"]}"
}

platform_context_has() {
    local namespace="$1"
    local key="$2"

    [[ -n "${PLATFORM_CONTEXT["${namespace}.${key}"]+x}" ]]
}

platform_context_namespace_exists() {
    local namespace="$1"

    [[ -n "${PLATFORM_CONTEXT["${namespace}.__namespace__"]+x}" ]]
}