# 14. Observabilidade

## Objetivo

A Observabilidade estabelece os mecanismos institucionais de monitoramento do Data Pipeline, permitindo acompanhar sua execução em tempo real, identificar falhas, medir desempenho e fornecer informações operacionais para administração da plataforma.

A observabilidade constitui uma capacidade nativa do Data Pipeline e deverá estar presente em todas as suas etapas.

---

## Escopo

A Observabilidade acompanha todo o ciclo operacional do pipeline.

```text
Acquisition
      │
Validation
      │
Transformation
      │
Normalization
      │
Enrichment
      │
Versioning
      │
Publication
```

Cada etapa deverá produzir informações suficientes para monitoramento operacional.

---

## Componentes

A infraestrutura de Observabilidade é composta por:

- Logging;
- Metrics;
- Tracing;
- Event Monitoring;
- Alerting;
- Dashboards Operacionais.

Cada componente possui responsabilidades específicas e complementares.

---

## Logging

Todos os componentes deverão registrar eventos relevantes da execução.

Os registros deverão conter, no mínimo:

- timestamp;
- Pipeline Execution ID;
- Dataset ID (quando aplicável);
- componente responsável;
- nível do log;
- mensagem;
- contexto da operação.

Os logs deverão ser estruturados e adequados para processamento automatizado.

---

## Métricas

O Data Pipeline deverá produzir métricas institucionais, incluindo:

- número de execuções;
- tempo médio de aquisição;
- tempo médio de validação;
- tempo médio de transformação;
- tempo médio de normalização;
- tempo médio de enriquecimento;
- tempo médio de versionamento;
- tempo médio de publicação;
- throughput;
- quantidade de registros processados;
- taxa de rejeição;
- taxa de sucesso;
- taxa de falhas.

As métricas deverão permitir análises históricas e comparativas.

---

## Tracing

Cada execução deverá possuir rastreamento distribuído entre todas as etapas do pipeline.

O tracing deverá permitir visualizar:

- sequência de execução;
- duração de cada etapa;
- dependências entre componentes;
- falhas;
- tempo total do processamento.

O Trace ID deverá estar associado ao Pipeline Execution ID.

---

## Monitoramento por Eventos

Os eventos publicados pelo Event Bus deverão ser monitorados em tempo real.

Exemplos:

- PipelineStarted;
- AcquisitionCompleted;
- ValidationFailed;
- DatasetPublished;
- PipelineCompleted.

Esses eventos alimentam mecanismos de supervisão operacional.

---

## Alertas

A arquitetura deverá permitir geração automática de alertas para situações como:

- falha de aquisição;
- indisponibilidade de fontes;
- rejeição excessiva de registros;
- degradação de desempenho;
- interrupção do pipeline;
- falha de publicação;
- erro de versionamento.

Os critérios de alerta deverão ser configuráveis.

---

## Dashboards Operacionais

A infraestrutura deverá disponibilizar informações consolidadas para acompanhamento operacional.

Exemplos de indicadores:

- pipelines ativos;
- execuções concluídas;
- execuções com falha;
- datasets publicados;
- tempo médio de processamento;
- filas pendentes;
- utilização de conectores;
- disponibilidade das fontes.

---

## Integração

A Observabilidade comunica-se com:

- Pipeline Runtime;
- Event Bus;
- Metadata Registry;
- Registry;
- Intelligence Core;
- infraestrutura corporativa de monitoramento.

Todas as integrações utilizam contratos públicos.

---

## Retenção

Logs, métricas e traces deverão seguir políticas institucionais de retenção definidas pela organização.

As políticas deverão considerar:

- requisitos legais;
- auditoria;
- desempenho;
- armazenamento;
- histórico operacional.

---

## Princípio Institucional

A Observabilidade constitui um requisito obrigatório do Data Pipeline.

Toda execução deverá produzir informações suficientes para monitoramento, diagnóstico, auditoria e melhoria contínua da plataforma, permitindo identificar rapidamente falhas operacionais e acompanhar a saúde do ecossistema de preparação de dados da Deja Indicadores.