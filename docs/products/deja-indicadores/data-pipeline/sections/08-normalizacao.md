# 08. Normalização

## Objetivo

A Normalização é responsável por padronizar os dados transformados segundo o modelo institucional da Deja Indicadores.

Seu objetivo é garantir que informações equivalentes provenientes de diferentes fontes sejam representadas de maneira uniforme, eliminando variações de nomenclatura, formatos, unidades e convenções.

O resultado desta etapa é o **Normalized Dataset**, que constitui a base oficial para enriquecimento e posterior publicação.

---

## Papel na Arquitetura

A Normalização sucede a Transformação e antecede o Enriquecimento.

```text
Transformed Dataset
        │
        ▼
 Normalization
        │
        ▼
Normalized Dataset
```

Após esta etapa, os dados passam a seguir exclusivamente o modelo institucional da plataforma.

---

## Responsabilidades

A Normalização possui as seguintes responsabilidades:

- padronizar nomenclaturas;
- unificar formatos;
- converter unidades de medida;
- padronizar datas e horários;
- padronizar moedas;
- uniformizar identificadores;
- consolidar códigos institucionais;
- eliminar representações equivalentes.

---

## Escopo

A Normalização atua sobre a representação dos dados.

Exemplos:

- nomes de campos;
- formatos de datas;
- formatos monetários;
- unidades físicas;
- códigos internos;
- identificadores;
- enumerações;
- valores booleanos.

Não fazem parte desta etapa:

- enriquecimento;
- inferências;
- cálculos;
- validações;
- regras de negócio.

---

## Estratégias de Normalização

### Padronização de Datas

Todas as datas deverão utilizar o formato institucional definido pela plataforma.

Exemplo:

```text
31/07/2026
2026-07-31
Jul 31, 2026
```

↓

```text
2026-07-31
```

---

### Padronização Monetária

Valores monetários deverão utilizar:

- moeda institucional;
- precisão definida;
- escala decimal padronizada.

---

### Padronização de Unidades

Unidades equivalentes deverão utilizar uma representação única.

Exemplos:

```text
Kg
kg
quilo
quilograma
```

↓

```text
kg
```

---

### Padronização de Enumerações

Representações equivalentes deverão convergir para valores institucionais.

Exemplo:

```text
Sim
S
Yes
True
1
```

↓

```text
TRUE
```

---

### Padronização de Identificadores

Identificadores institucionais deverão seguir convenções únicas.

Exemplos:

- códigos de indicadores;
- códigos de organizações;
- identificadores de datasets;
- identificadores de execução.

---

## Catálogos Institucionais

A Normalização poderá consultar:

- Indicator Catalog;
- Knowledge Base;
- tabelas institucionais;
- dicionários corporativos.

Esses componentes fornecem as referências oficiais para padronização.

---

## Regras de Normalização

Todas as regras deverão ser:

- declarativas;
- versionadas;
- reutilizáveis;
- auditáveis;
- rastreáveis.

Cada regra deverá possuir identificador e histórico de evolução.

---

## Metadados Produzidos

Ao término da execução deverão ser registrados:

- versão das regras;
- quantidade de registros normalizados;
- quantidade de normalizações aplicadas;
- duração;
- falhas;
- Pipeline Execution ID.

---

## Eventos

A etapa poderá publicar:

- NormalizationStarted;
- NormalizationCompleted;
- DatasetNormalized;
- NormalizationRuleApplied;
- NormalizationFailed.

Todos os eventos utilizam o Event Bus institucional.

---

## Integração

A Normalização comunica-se com:

- Pipeline Runtime;
- Pipeline Context;
- Registry;
- Event Bus;
- Metadata Registry;
- Observability;
- Indicator Catalog;
- Knowledge Base.

O resultado produzido é o **Normalized Dataset**, consumido pela etapa de Enriquecimento.

---

## Princípio Institucional

Todo dado disponibilizado pela Deja Indicadores deverá possuir representação institucional única.

A Normalização elimina diferenças de representação entre fontes distintas, permitindo que todos os componentes da plataforma operem sobre um modelo uniforme, consistente e independente da origem dos dados.