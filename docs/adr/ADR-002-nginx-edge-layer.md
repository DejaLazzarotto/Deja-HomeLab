# ADR-002 — NGINX como Edge Layer da Deja Platform

## Status

Accepted

## Data

2026-06-25

## Contexto

A Deja Platform hospeda múltiplas aplicações web, APIs e serviços em um único servidor (Node 01 — Orion).

É necessário estabelecer um ponto único de entrada para controlar:

- publicação das aplicações;
- certificados SSL/TLS;
- proxy reverso;
- redirecionamentos HTTP → HTTPS;
- domínios e subdomínios;
- isolamento entre aplicações.

## Decisão

O NGINX será adotado como o componente oficial de Edge Layer da Deja Platform.

Todas as aplicações publicadas externamente deverão ser acessadas através do NGINX.

Nenhuma aplicação deverá expor portas diretamente para a Internet, exceto quando existir uma justificativa arquitetural documentada em uma ADR.

## Consequências

### Benefícios

- Padronização da publicação de aplicações.
- Centralização da configuração HTTPS.
- Simplificação do gerenciamento de certificados.
- Facilidade para adicionar novos serviços.
- Menor acoplamento entre infraestrutura e aplicações.

### Desvantagens

- O NGINX torna-se um componente crítico da plataforma.
- Configurações incorretas podem impactar múltiplos serviços.

## Alternativas consideradas

- Apache HTTP Server
- Caddy
- Traefik

O NGINX foi escolhido por sua maturidade, desempenho, ampla documentação e compatibilidade com os objetivos da Deja Platform.

## Relação com outras ADRs

- ADR-001 — Platform Architecture