# Official Module Structure

## Status

Official

---

# Purpose

This document defines the recommended directory structure for modules developed with the Deja Platform Public Module SDK.

The structure described here is the reference implementation adopted by the official examples.

---

# Recommended Layout

```text
example/
├── manifest.yaml
├── module.sh
├── commands/
│   └── hello.sh
├── config/
│   └── default.yaml
└── README.md
```

---

# Design Principles

The recommended structure follows these principles:

- One responsibility per directory.
- Predictable file locations.
- Clear separation between resources.
- Compatibility with the Public Module SDK.
- No dependency on Kernel internals.

---

# Notes

Modules may include additional directories when necessary.

However, the organization presented here is the recommended starting point for all new modules.
```