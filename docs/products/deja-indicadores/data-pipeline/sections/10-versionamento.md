# 10. Versionamento

## Objetivo

O Versionamento é responsável por preservar a evolução dos conjuntos de dados produzidos pelo Data Pipeline.

Seu objetivo é garantir reprodutibilidade, auditoria, rastreabilidade e compatibilidade entre diferentes execuções do ecossistema de inteligência da Deja Indicadores.

Cada conjunto de dados publicado torna-se um artefato institucional versionado.

---

## Papel na Arquitetura

O Versionamento sucede o Enriquecimento e antecede a Publicação.

```text
Enriched Dataset
        │
        ▼
   Versioning
        │
        ▼
Versioned Dataset
```

A partir desta etapa, cada Dataset passa a possuir identidade própria e histórico permanente.

---

## Responsabilidades

O Versionamento possui as seguintes responsabilidades:

- gerar identificadores únicos;
- controlar versões dos datasets;
- preservar histórico;
- manter compatibilidade;
- registrar lineage;
- produzir snapshots;
- permitir reconstrução histórica;
- disponibilizar metadados de evolução.

---

## Dataset Version

Cada conjunto de dados deverá possuir um identificador institucional.

Exemplo:

```text
DATASET-INDICATORS
    Version 1.0.0

DATASET-FATURAMENTO
    Version 2.3.1
```

A versão identifica exatamente o conteúdo disponibilizado pelo pipeline.

---

## Estratégia de Versionamento

O Data Pipeline adota versionamento explícito.

Toda alteração publicada gera uma nova versão.

Nenhuma versão publicada poderá ser modificada posteriormente.

Caso sejam necessárias alterações, deverá ser criada uma nova versão.

---

## Imutabilidade

Datasets publicados são imutáveis.

Essa característica garante:

- auditoria;
- reprodutibilidade;
- rastreabilidade;
- consistência histórica.

---

## Lineage

Cada versão deverá manter o histórico completo de sua origem.

O lineage deverá registrar, no mínimo:

- fontes utilizadas;
- Pipeline Execution ID;
- regras aplicadas;
- transformações;
- normalizações;
- enriquecimentos;
- versões dos componentes utilizados.

---

## Snapshots

O Versionamento poderá produzir snapshots completos dos datasets.

Esses snapshots permitem:

- reconstrução histórica;
- auditorias;
- testes;
- comparação entre versões;
- recuperação operacional.

---

## Compatibilidade

A evolução dos datasets deverá preservar compatibilidade sempre que possível.

Mudanças incompatíveis deverão ser claramente identificadas e documentadas.

---

## Política de Retenção

A arquitetura poderá definir políticas para:

- retenção de versões;
- arquivamento;
- descarte controlado;
- armazenamento histórico.

A política institucional deverá preservar os requisitos legais e operacionais da organização.

---

## Metadados Produzidos

Cada versão deverá registrar, no mínimo:

- Dataset ID;
- versão;
- Pipeline Execution ID;
- timestamp;
- origem;
- quantidade de registros;
- hash do conteúdo;
- lineage;
- regras utilizadas;
- status da publicação.

---

## Eventos

O Versionamento poderá publicar:

- DatasetVersionCreated;
- DatasetVersionPublished;
- DatasetVersionArchived;
- DatasetVersionDeprecated;
- DatasetVersionRestored.

Todos os eventos utilizam o Event Bus institucional.

---

## Integração

O Versionamento comunica-se com:

- Pipeline Runtime;
- Pipeline Context;
- Metadata Registry;
- Registry;
- Event Bus;
- Observability;
- Publication.

Seu resultado é o **Versioned Dataset**, encaminhado para publicação oficial.

---

## Princípio Institucional

Todo conjunto de dados produzido pela Deja Indicadores deverá possuir identificação única, histórico permanente e versionamento explícito.

O Versionamento constitui a base institucional para auditoria, reprodutibilidade, rastreabilidade e evolução segura do ecossistema de inteligência, assegurando que qualquer processamento possa ser reconstruído utilizando exatamente a mesma versão dos dados originalmente publicada.