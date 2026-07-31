# 10. Políticas e Governança

## Objetivo

Esta seção descreve a arquitetura institucional de políticas e governança de segurança da Deja Platform.

A governança estabelece os mecanismos responsáveis por definir, aplicar, controlar e evoluir as regras de segurança utilizadas por todos os componentes da plataforma.

---

# Conceito de governança

A governança de segurança representa o conjunto de processos, políticas e controles utilizados para garantir que a plataforma opere de acordo com requisitos institucionais de proteção.

---

# Security Policy Registry

## Responsabilidade

O Security Policy Registry mantém o catálogo centralizado das políticas de segurança da plataforma.

---

## Capacidades

Inclui:

- criação de políticas;
- armazenamento;
- versionamento;
- publicação;
- consulta;
- histórico de alterações.

---

# Tipos de políticas

O Security suporta diferentes categorias de políticas.

## Políticas de identidade

Definem regras relacionadas a:

- criação de identidades;
- atributos obrigatórios;
- ciclo de vida;
- validações.

---

## Políticas de autenticação

Definem requisitos para:

- métodos permitidos;
- níveis de confiança;
- expiração;
- validação adicional.

---

## Políticas de autorização

Definem:

- permissões;
- recursos protegidos;
- operações permitidas;
- restrições de acesso.

---

## Políticas de dados

Definem controles sobre:

- classificação;
- proteção;
- retenção;
- compartilhamento.

---

## Políticas operacionais

Definem requisitos para:

- serviços;
- integrações;
- componentes;
- ambientes.

---

# Versionamento de políticas

Toda política deve possuir:

- identificador único;
- versão;
- data de criação;
- responsável;
- histórico de alterações;
- estado de publicação.

---

# Aplicação de políticas

As políticas são aplicadas pelos componentes responsáveis pela decisão de segurança.

Fluxo:
