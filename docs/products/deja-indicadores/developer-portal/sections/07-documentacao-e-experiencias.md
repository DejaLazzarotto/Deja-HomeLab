# 07. Documentação e Experiências

## Objetivo

Esta seção define a arquitetura responsável pela documentação e pelas experiências de integração oferecidas pelo Developer Portal da Deja Platform.

O objetivo é garantir que consumidores tenham acesso às informações necessárias para compreender, avaliar e utilizar as APIs disponibilizadas pela plataforma.

---

# Papel da documentação

A documentação é considerada um recurso arquitetural da API.

Ela não representa apenas material auxiliar, mas parte integrante do ciclo de vida da API.

Cada API publicada deve possuir documentação adequada ao seu contexto de utilização.

---

# Tipos de documentação

O Developer Portal deve suportar diferentes tipos de documentação.

## Documentação funcional

Apresenta:

- objetivo da API;
- capacidade atendida;
- casos de uso;
- regras de negócio;
- limitações.

---

## Documentação técnica

Apresenta:

- contratos;
- endpoints;
- modelos de dados;
- parâmetros;
- códigos de resposta;
- requisitos técnicos.

---

## Documentação operacional

Apresenta:

- disponibilidade;
- limites de consumo;
- políticas aplicáveis;
- comportamento esperado;
- informações de suporte.

---

# Modelo de documentação

Cada API deve possuir uma estrutura organizada:

```text
API

+--------------------------------+
| Visão geral                    |
+--------------------------------+
| Conceitos                      |
+--------------------------------+
| Autenticação                   |
+--------------------------------+
| Referência técnica             |
+--------------------------------+
| Exemplos                       |
+--------------------------------+
| Limitações                     |
+--------------------------------+
| Histórico de versões           |
+--------------------------------+