# 14. Auditoria

## Objetivo

Esta seção descreve os mecanismos de auditoria aplicados ao Configuration da Deja Platform.

A auditoria garante visibilidade completa sobre operações configuracionais, permitindo controle, investigação, conformidade e análise histórica.

---

# Conceito de auditoria configuracional

A auditoria registra eventos relacionados ao ciclo de vida das configurações.

Seu objetivo é preservar evidências sobre:

- alterações;
- acessos;
- decisões;
- aprovações;
- publicações;
- falhas.

---

# Configuration Audit Service

O Configuration Audit Service é responsável pelo registro das operações auditáveis.

Responsabilidades:

- capturar eventos;
- armazenar evidências;
- correlacionar operações;
- disponibilizar consultas.

---

# Eventos auditáveis

Devem ser registrados:

## Criação

Inclui:

- configuração criada;
- responsável;
- origem;
- contexto;
- versão inicial.

---

## Alteração

Inclui:

- configuração modificada;
- valores anteriores;
- novos valores;
- justificativa;
- responsável.

---

## Validação

Inclui:

- regras executadas;
- resultado;
- erros encontrados;
- momento da validação.

---

## Aprovação

Inclui:

- aprovador;
- decisão;
- justificativa;
- política aplicada.

---

## Publicação

Inclui:

- versão publicada;
- ambiente;
- consumidores impactados.

---

## Consulta

Quando necessário, acessos a configurações sensíveis devem ser auditados.

---

# Modelo de registro de auditoria

Modelo conceitual:
