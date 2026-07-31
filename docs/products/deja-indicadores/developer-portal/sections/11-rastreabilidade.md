# 11. Rastreabilidade

## Objetivo

Esta seção define os mecanismos de rastreabilidade aplicados ao Developer Portal da Deja Platform.

O objetivo é garantir que todas as interações relevantes envolvendo APIs, consumidores, acessos e operações do Portal possam ser identificadas, acompanhadas e auditadas.

---

# Princípio de rastreabilidade

Toda operação relevante deve possuir contexto suficiente para responder:

- quem realizou a ação;
- qual recurso foi envolvido;
- quando ocorreu;
- qual operação foi executada;
- qual resultado foi obtido.

A rastreabilidade é requisito institucional da plataforma.

---

# Elementos rastreáveis

O Developer Portal deve preservar informações relacionadas a:

## Consumidores

Inclui:

- identidade;
- organização;
- perfil;
- relacionamento com APIs;
- histórico de ações.

---

## APIs

Inclui:

- identificador;
- versão;
- estado;
- documentação associada;
- histórico de publicação.

---

## Acessos

Inclui:

- solicitação;
- aprovação;
- rejeição;
- alteração;
- revogação.

---

## Operações do Portal

Inclui:

- consultas;
- alterações;
- publicações;
- solicitações;
- interações administrativas.

---

# Integração com Execution Log

O Execution Log registra eventos técnicos relacionados às operações do Developer Portal.

Exemplos:

```text id="1k6p9z"
API visualizada

Documentação acessada

Acesso solicitado

Consumidor criado

Permissão alterada

Configuração modificada