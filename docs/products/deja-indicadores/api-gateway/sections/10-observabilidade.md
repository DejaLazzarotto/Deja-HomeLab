# 10. Observabilidade

## Objetivo

Esta seção descreve o modelo de observabilidade aplicado ao API Gateway da Deja Platform.

O objetivo é garantir visibilidade completa sobre chamadas, desempenho, comportamento, falhas e operações realizadas através das APIs.

---

# Visão geral

A observabilidade do API Gateway é uma capacidade nativa e obrigatória.

Toda chamada deve gerar informações suficientes para:

- monitoramento;
- diagnóstico;
- análise operacional;
- auditoria;
- evolução da plataforma.

---

# Princípios de observabilidade

A observabilidade segue os princípios:

- coleta automática;
- rastreabilidade ponta a ponta;
- correlação de eventos;
- diagnóstico orientado a contexto;
- integração institucional.

---

# Tipos de telemetria

O API Gateway produz três tipos principais de telemetria:

- métricas;
- logs;
- traces.

Esses elementos trabalham em conjunto para fornecer visão operacional completa.

---

# Métricas

As métricas representam informações quantitativas sobre o funcionamento do Gateway.

Exemplos:

- quantidade de chamadas;
- tempo médio de resposta;
- taxa de erro;
- volume por API;
- consumo por versão;
- disponibilidade.

---

# Logs

Os logs registram eventos técnicos relevantes.

Podem incluir:

- recebimento de requisição;
- autenticação;
- autorização;
- roteamento;
- despacho;
- retorno;
- falhas.

Os registros devem possuir contexto suficiente para análise.

---

# Traces

Os traces permitem acompanhar uma chamada através dos componentes envolvidos.

Um trace pode representar:
