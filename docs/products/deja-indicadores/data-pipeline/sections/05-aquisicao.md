# 05. Aquisição

## Objetivo

A Aquisição representa a etapa responsável por obter dados das fontes registradas no Data Pipeline e convertê-los em um conjunto de dados bruto (Raw Dataset) apto para iniciar o processamento institucional.

Esta etapa coordena a comunicação com os Source Connectors, controla a execução das coletas e produz o primeiro artefato oficial do pipeline.

---

## Papel na Arquitetura

A Aquisição constitui o ponto de entrada do Data Pipeline.

Nenhuma etapa posterior comunica-se diretamente com as fontes de dados.

O fluxo institucional é:

```text
Source
   │
   ▼
Source Connector
   │
   ▼
Acquisition
   │
   ▼
Raw Dataset
```

A partir desse momento, todas as etapas trabalham exclusivamente sobre os dados adquiridos.

---

## Responsabilidades

A Aquisição possui as seguintes responsabilidades institucionais:

- iniciar a coleta;
- coordenar os Source Connectors;
- controlar autenticação;
- controlar paginação;
- controlar processamento incremental;
- controlar limites de leitura;
- registrar metadados;
- produzir o Raw Dataset;
- registrar eventos de execução.

---

## Raw Dataset

O resultado da Aquisição é denominado **Raw Dataset**.

Este conjunto representa fielmente os dados retornados pela fonte, preservando sua estrutura original.

Nesta etapa não são realizadas:

- validações de negócio;
- normalizações;
- enriquecimentos;
- conversões semânticas.

O objetivo é preservar a integridade da origem.

---

## Estratégias de Aquisição

O Data Pipeline suporta diferentes estratégias de coleta.

### Aquisição Completa

Obtém todos os registros disponíveis na fonte.

Indicada para:

- primeira carga;
- reconstrução;
- sincronização completa.

---

### Aquisição Incremental

Obtém apenas os registros alterados desde a última execução.

Pode utilizar:

- timestamps;
- versões;
- identificadores;
- cursores;
- eventos.

Esta é a estratégia preferencial sempre que suportada pela fonte.

---

### Aquisição Sob Demanda

Executada mediante solicitação explícita de outro componente.

Utilizada em:

- reprocessamentos;
- testes;
- diagnósticos;
- sincronizações específicas.

---

### Aquisição Agendada

Executada automaticamente conforme políticas institucionais.

Exemplos:

- diária;
- horária;
- semanal;
- mensal;
- personalizada.

O agendamento é responsabilidade do Runtime do Data Pipeline.

---

## Controle de Execução

Cada execução deverá possuir um identificador único (Pipeline Execution ID).

Exemplo:

```text
PIPELINE-EXEC-20260731-000145
```

Esse identificador acompanhará todas as etapas subsequentes.

---

## Metadados Produzidos

Ao término da Aquisição deverão ser registrados, no mínimo:

- Pipeline Execution ID;
- Source ID;
- Connector ID;
- início da execução;
- término da execução;
- duração;
- quantidade de registros;
- estratégia utilizada;
- versão do conector;
- status da execução.

Esses metadados alimentam os mecanismos de observabilidade e rastreabilidade.

---

## Tratamento de Falhas

A Aquisição deverá identificar e tratar situações como:

- falha de autenticação;
- indisponibilidade da fonte;
- timeout;
- interrupção da comunicação;
- dados incompletos;
- inconsistência estrutural;
- limite excedido;
- erro do conector.

Sempre que possível, a execução deverá permitir retomada (resume) sem perda de consistência.

---

## Eventos Gerados

Durante a Aquisição poderão ser publicados eventos como:

- AcquisitionStarted;
- AcquisitionCompleted;
- AcquisitionFailed;
- AcquisitionRetried;
- RawDatasetCreated.

Esses eventos são distribuídos pelo Event Bus institucional.

---

## Integração

A Aquisição comunica-se com:

- Source Connectors;
- Pipeline Runtime;
- Pipeline Context;
- Event Bus;
- Observability;
- Registry.

Não existe comunicação direta com os Engines especializados.

---

## Princípio Institucional

Toda aquisição de dados da Deja Indicadores deverá produzir um Raw Dataset íntegro, reproduzível, rastreável e independente das regras de negócio da plataforma.

A Aquisição representa exclusivamente a obtenção dos dados, preservando sua fidelidade à origem e preparando-os para as etapas posteriores de validação, transformação e qualificação.