# 13. Rastreabilidade

## Objetivo

A Rastreabilidade estabelece os mecanismos institucionais para registrar e reconstruir todo o ciclo de vida dos dados processados pelo Data Pipeline.

Seu objetivo é permitir auditoria completa, reprodutibilidade, investigação de incidentes e comprovação da origem de qualquer informação utilizada pela Deja Indicadores.

Todo Dataset deverá possuir rastreabilidade de ponta a ponta.

---

## Escopo

A rastreabilidade cobre todas as etapas do processamento:

```text
Source
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
   │
   ▼
Intelligence Core
   │
   ▼
Specialized Engines
```

Cada transição deverá gerar evidências suficientes para reconstrução completa da execução.

---

## Identificação da Execução

Toda execução do Data Pipeline deverá possuir um identificador institucional único.

Exemplo:

```text
PIPELINE-EXEC-20260731-000145
```

Esse identificador acompanhará todas as etapas do processamento.

---

## Lineage

Cada Dataset publicado deverá manter seu histórico completo de origem (Data Lineage).

O Lineage deverá registrar, no mínimo:

- Source ID;
- Connector ID;
- Pipeline Execution ID;
- versões das regras aplicadas;
- componentes utilizados;
- datasets intermediários;
- Dataset Version;
- Published Dataset.

---

## Evidências

Cada etapa deverá produzir evidências institucionais.

Exemplos:

- início da execução;
- término;
- duração;
- parâmetros utilizados;
- regras aplicadas;
- eventos publicados;
- métricas produzidas;
- erros encontrados.

Essas evidências integram o histórico permanente do Dataset.

---

## Rastreabilidade das Regras

Sempre que uma regra for aplicada deverá ser possível identificar:

- identificador da regra;
- versão;
- etapa do pipeline;
- data da execução;
- resultado produzido.

Essa informação permite reproduzir exatamente o processamento realizado.

---

## Rastreabilidade das Fontes

Toda informação publicada deverá indicar claramente sua origem.

Os registros mínimos incluem:

- Source ID;
- tipo da fonte;
- versão do conector;
- instante da aquisição;
- estratégia utilizada;
- quantidade de registros coletados.

---

## Rastreabilidade dos Datasets

Cada Dataset deverá possuir identificação permanente contendo, no mínimo:

- Dataset ID;
- versão;
- Pipeline Execution ID;
- timestamp;
- hash;
- lineage;
- status;
- origem.

---

## Auditoria

A arquitetura deverá permitir responder perguntas como:

- Qual fonte originou este Dataset?
- Quando foi produzido?
- Quais regras foram aplicadas?
- Qual versão do pipeline foi utilizada?
- Quais componentes participaram da execução?
- Qual versão foi consumida pelo Intelligence Core?
- Quais Engines utilizaram esse Dataset?

---

## Integração

A rastreabilidade integra-se com:

- Pipeline Runtime;
- Metadata Registry;
- Event Bus;
- Observability;
- Versioning;
- Publication;
- Intelligence Core.

Esses componentes compartilham informações por meio de contratos institucionais.

---

## Princípio Institucional

Toda informação disponibilizada pela Deja Indicadores deverá possuir origem conhecida, processamento documentado, histórico permanente e capacidade de reconstrução completa.

A Rastreabilidade constitui um requisito arquitetural obrigatório e deverá acompanhar todo o ciclo de vida dos dados, desde a aquisição até seu consumo pelos componentes de inteligência da plataforma.