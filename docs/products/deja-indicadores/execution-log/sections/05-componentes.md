# 5. Componentes

## Objetivo

Esta seção descreve os principais componentes que compõem a arquitetura do Execution Log.

Cada componente possui responsabilidade única, interfaces bem definidas e baixo acoplamento, permitindo evolução independente e alta escalabilidade.

---

## Visão geral

A arquitetura do Execution Log é composta pelos seguintes componentes:

- Log Receiver;
- Log Validator;
- Log Enricher;
- Log Classifier;
- Log Repository;
- Log Indexer;
- Query Engine;
- Retention Manager;
- Archive Manager;
- Audit Manager.

Cada componente participa de uma etapa específica do ciclo de vida dos registros técnicos.

---

## Log Receiver

O Log Receiver constitui o ponto oficial de entrada dos registros técnicos.

Suas responsabilidades incluem:

- receber eventos produzidos pelos componentes autorizados;
- validar o formato básico da requisição;
- encaminhar os registros para processamento;
- desacoplar os produtores da infraestrutura de armazenamento.

---

## Log Validator

O Log Validator verifica a consistência estrutural dos registros recebidos.

Entre suas responsabilidades estão:

- validar campos obrigatórios;
- verificar conformidade com o modelo institucional;
- identificar registros inválidos;
- aplicar regras institucionais de validação.

---

## Log Enricher

O Log Enricher complementa os registros com informações institucionais.

Pode adicionar automaticamente:

- timestamp institucional;
- identificadores de correlação;
- contexto da execução;
- ambiente;
- metadados operacionais;
- informações de infraestrutura.

Esse enriquecimento reduz a responsabilidade dos componentes produtores de logs.

---

## Log Classifier

O Log Classifier determina a classificação institucional de cada registro.

Entre os critérios utilizados podem estar:

- nível de severidade;
- categoria;
- componente;
- domínio funcional;
- tipo do evento;
- criticidade operacional.

Essa classificação facilita consultas e monitoramento.

---

## Log Repository

O Log Repository é responsável pela persistência dos registros.

Suas responsabilidades incluem:

- armazenamento estruturado;
- preservação da integridade;
- suporte às políticas institucionais de retenção;
- abstração da tecnologia de armazenamento.

---

## Log Indexer

O Log Indexer mantém os índices necessários para consultas eficientes.

A indexação pode considerar:

- período;
- severidade;
- componente;
- execução;
- workflow;
- usuário;
- categoria;
- ambiente.

A estratégia de indexação permanece independente do mecanismo de persistência.

---

## Query Engine

O Query Engine disponibiliza mecanismos padronizados de pesquisa dos registros.

Entre suas funções:

- consultas estruturadas;
- filtros;
- ordenação;
- paginação;
- agregações;
- consultas históricas.

---

## Retention Manager

O Retention Manager aplica as políticas institucionais de retenção.

Entre suas responsabilidades:

- retenção por período;
- retenção por categoria;
- retenção por severidade;
- eliminação controlada;
- conformidade com políticas corporativas.

---

## Archive Manager

O Archive Manager administra o arquivamento dos registros técnicos.

Suas funções incluem:

- movimentação para armazenamento de longo prazo;
- preservação da integridade;
- recuperação de registros arquivados;
- suporte a auditorias futuras.

---

## Audit Manager

O Audit Manager supervisiona as operações realizadas sobre a infraestrutura de logs.

Entre elas:

- consultas realizadas;
- alterações de configuração;
- políticas aplicadas;
- operações de retenção;
- arquivamentos;
- recuperações.

Esse componente reforça a governança e a rastreabilidade operacional.

---

## Cooperação entre componentes

Os componentes cooperam de forma sequencial e desacoplada.

Essa organização permite substituir tecnologias de persistência, indexação, consulta ou arquivamento sem alterar os contratos públicos da arquitetura, preservando a estabilidade e a evolução contínua do Execution Log.