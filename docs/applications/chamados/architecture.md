# Arquitetura — Deja Chamados

## Visão geral

O Chamados é um módulo funcional da Deja Platform, com backend FastAPI e frontend Angular.

## Backend

- Repositório: `deja-indicadores-api`
- Framework: FastAPI
- Persistência: SQLAlchemy 2
- Banco de dados: MySQL
- API base: `/api/chamados`

## Frontend

- Repositório: `workspace`
- Framework: Angular
- Modelo: domínio, aplicação, infraestrutura e apresentação
- Rotas principais: workspace e portal do cliente

## Domínios principais

- Clientes
- Tickets
- Responsáveis
- Comentários
- Anexos
- Timeline
- Portal do cliente
- Fila de atendimento
- Dashboard

## Perfis de autorização

- `platform_admin`
- `organization_admin`
- `tenant_admin`
- `manager`
- `analyst`
- `viewer`
- `client` para acesso ao portal externo

## Observação

Este documento será completado durante a auditoria final da migração.
