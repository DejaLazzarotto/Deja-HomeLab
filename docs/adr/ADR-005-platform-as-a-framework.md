# ADR-005 — Platform as a Framework

## Status

Accepted

## Context

A Deja Platform evoluiu de uma CLI para um Framework de gerenciamento de infraestrutura e aplicações.

O Kernel passa a fornecer APIs públicas estáveis para módulos, mantendo as implementações internas privadas.

## Decision

A plataforma será estruturada em:

- Bootstrap
- Command System
- Module System
- Kernel

O Kernel será a única camada responsável por disponibilizar serviços comuns através de APIs públicas.

Nenhum módulo poderá acessar implementações internas do Kernel.

## Consequences

Benefícios:

- baixo acoplamento;
- alta coesão;
- APIs estáveis;
- facilidade de evolução;
- compatibilidade entre versões;
- possibilidade de múltiplas interfaces (CLI e futuras interfaces gráficas).