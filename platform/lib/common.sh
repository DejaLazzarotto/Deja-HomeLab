#!/usr/bin/env bash

platform_error() {
    echo "Erro: $1" >&2
    exit 1
}

platform_info() {
    echo "$1"
}