# 03. Organização

## Objetivo

O Data Pipeline é organizado como uma infraestrutura modular composta por componentes especializados, cada um responsável por uma etapa específica do ciclo de preparação dos dados.

Essa organização reduz o acoplamento entre as fases do processamento, facilita a evolução incremental da arquitetura e permite reutilização dos componentes em diferentes cenários.

---

## Organização Geral

A arquitetura institucional é composta pelos seguintes módulos:

```text
Data Pipeline
│
├── Source Connectors
├── Acquisition
├── Validation
├── Transformation
├── Normalization
├── Enrichment
├── Versioning
├── Publication
├── Metadata
├── Runtime
├── Context
├── Event Bus
├── Registry
└── Observability
```

Cada módulo possui responsabilidade única, contratos bem definidos e integração através do Intelligence Core.

---

## Source Connectors

Responsável pela comunicação com as diferentes fontes de dados.

Suas responsabilidades incluem:

- estabelecer conexões;
- autenticação;
- leitura de dados;
- tratamento de falhas de comunicação;
- adaptação ao formato nativo da origem.

Os conectores não executam transformações de negócio.

---

## Acquisition

Responsável pela aquisição controlada dos dados provenientes dos conectores.

Executa:

- orquestração da coleta;
- controle de execução;
- processamento incremental;
- controle de lotes;
- recuperação de falhas.

---

## Validation

Responsável pela verificação da qualidade dos dados.

Inclui:

- validação estrutural;
- validação de tipos;
- validação de domínio;
- integridade;
- consistência;
- completude.

Dados inválidos não avançam para as próximas etapas.

---

## Transformation

Executa adaptações necessárias para converter os dados ao modelo institucional.

Exemplos:

- conversão de formatos;
- reorganização estrutural;
- padronização de unidades;
- tratamento de valores.

---

## Normalization

Padroniza os dados para consumo uniforme por toda a plataforma.

Entre suas responsabilidades:

- padronização de nomenclaturas;
- formatos de data;
- moedas;
- unidades;
- identificadores;
- codificações.

---

## Enrichment

Adiciona informações derivadas ou complementares aos dados processados.

Pode utilizar:

- catálogos internos;
- tabelas auxiliares;
- metadados;
- conhecimento institucional.

---

## Versioning

Responsável pela geração e gerenciamento das versões dos conjuntos de dados publicados.

Mantém:

- histórico;
- identificação;
- lineage;
- snapshots;
- compatibilidade.

---

## Publication

Disponibiliza oficialmente os conjuntos de dados para consumo.

Somente dados aprovados poderão ser publicados.

A publicação representa o encerramento do pipeline de preparação.

---

## Metadata

Gerencia todas as informações descritivas do processamento.

Inclui:

- origem;
- timestamps;
- versões;
- qualidade;
- lineage;
- responsáveis;
- configuração utilizada.

---

## Runtime

Coordena a execução operacional do Data Pipeline.

Responsável por:

- iniciar execuções;
- controlar estados;
- executar etapas;
- registrar eventos;
- controlar falhas.

---

## Context

Representa o estado compartilhado da execução corrente.

Armazena:

- configuração;
- metadados;
- artefatos temporários;
- resultados intermediários;
- informações de execução.

---

## Event Bus

Realiza a comunicação desacoplada entre os módulos do pipeline.

Eventos incluem:

- início;
- término;
- falhas;
- validações;
- publicação;
- versionamento;
- monitoramento.

---

## Registry

Centraliza o registro dos componentes institucionais.

Permite descoberta dinâmica de:

- conectores;
- validadores;
- transformadores;
- enriquecedores;
- publicadores;
- observadores.

---

## Observability

Responsável pelo monitoramento operacional do pipeline.

Inclui:

- logs;
- métricas;
- tracing;
- auditoria;
- eventos;
- indicadores de desempenho.

---

## Fluxo Arquitetural

```text
Connectors
      │
      ▼
Acquisition
      │
      ▼
Validation
      │
      ▼
Transformation
      │
      ▼
Normalization
      │
      ▼
Enrichment
      │
      ▼
Versioning
      │
      ▼
Publication
```

Cada módulo opera de forma independente, comunicando-se através de contratos institucionais e preservando o desacoplamento da arquitetura.

---

## Organização Institucional

A estrutura modular do Data Pipeline estabelece um pipeline único, reutilizável, extensível e observável para toda a Deja Indicadores.

Novas capacidades deverão ser incorporadas por meio da evolução dos módulos existentes ou da introdução de novos componentes especializados, preservando sempre a separação de responsabilidades e os princípios arquiteturais definidos para a plataforma.