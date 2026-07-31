# 09. Enriquecimento

## Objetivo

O Enriquecimento é responsável por complementar o **Normalized Dataset** com informações adicionais provenientes de fontes institucionais, aumentando seu contexto, qualidade e valor para consumo pelo Intelligence Core e pelos Engines especializados.

Esta etapa não altera o significado original dos dados, apenas adiciona informações relevantes para sua interpretação e utilização.

O resultado produzido é denominado **Enriched Dataset**.

---

## Papel na Arquitetura

O Enriquecimento sucede a Normalização e antecede o Versionamento.

```text
Normalized Dataset
        │
        ▼
   Enrichment
        │
        ▼
Enriched Dataset
```

Após esta etapa, o conjunto de dados encontra-se completo para publicação institucional.

---

## Responsabilidades

O Enriquecimento possui as seguintes responsabilidades:

- adicionar metadados institucionais;
- complementar informações utilizando catálogos oficiais;
- resolver referências entre entidades;
- incluir classificações;
- incorporar atributos derivados;
- anexar informações contextuais;
- registrar evidências do enriquecimento.

---

## Fontes de Enriquecimento

O Data Pipeline poderá utilizar diferentes fontes institucionais.

### Indicator Catalog

Fornece:

- identificadores oficiais;
- classificações;
- categorias;
- unidades;
- fórmulas;
- metadados dos indicadores.

---

### Knowledge Base

Disponibiliza:

- conceitos;
- terminologia;
- relacionamentos;
- conhecimento reutilizável;
- definições institucionais.

---

### Tabelas Institucionais

Incluem:

- domínios controlados;
- códigos internos;
- classificações organizacionais;
- parâmetros corporativos.

---

### Serviços Especializados

O pipeline poderá consultar serviços responsáveis por fornecer informações complementares, desde que homologados pela arquitetura institucional.

---

## Tipos de Enriquecimento

### Classificação

Associa categorias oficiais aos dados.

Exemplos:

- categoria;
- segmento;
- criticidade;
- área de negócio.

---

### Associação

Relaciona entidades previamente independentes.

Exemplos:

- organização;
- unidade;
- indicador;
- processo;
- usuário.

---

### Complementação

Inclui atributos inexistentes na origem.

Exemplos:

- descrição;
- unidade de medida;
- responsável;
- classificação oficial.

---

### Derivação

Produz novos atributos a partir dos dados existentes, sem alterar o conteúdo original.

Exemplos:

- faixas;
- agrupamentos;
- códigos derivados;
- identificadores institucionais.

---

## Regras de Enriquecimento

Todas as regras deverão ser:

- declarativas;
- versionadas;
- auditáveis;
- reproduzíveis;
- rastreáveis.

Cada regra deverá possuir:

- identificador;
- versão;
- origem;
- descrição;
- histórico.

---

## Integridade

O Enriquecimento não poderá modificar o valor original dos dados provenientes da Normalização.

Informações adicionais deverão ser incorporadas como novos atributos ou metadados, preservando integralmente o conteúdo original.

---

## Metadados Produzidos

Ao término da execução deverão ser registrados:

- Pipeline Execution ID;
- versão das regras de enriquecimento;
- fontes consultadas;
- quantidade de atributos adicionados;
- duração;
- falhas encontradas;
- evidências produzidas.

---

## Eventos

O Enriquecimento poderá publicar eventos como:

- EnrichmentStarted;
- EnrichmentCompleted;
- EnrichmentFailed;
- DatasetEnriched;
- EnrichmentRuleApplied.

Todos os eventos são distribuídos pelo Event Bus institucional.

---

## Integração

O Enriquecimento comunica-se com:

- Pipeline Runtime;
- Pipeline Context;
- Knowledge Base;
- Indicator Catalog;
- Metadata Registry;
- Registry;
- Event Bus;
- Observability.

Seu resultado é o **Enriched Dataset**, encaminhado para a etapa de Versionamento.

---

## Princípio Institucional

O Enriquecimento representa a etapa responsável por agregar conhecimento institucional aos dados preparados pelo Data Pipeline.

Toda informação complementar deverá possuir origem conhecida, regras versionadas, rastreabilidade completa e preservação integral dos dados originais, garantindo que o ecossistema de inteligência opere sobre conjuntos de dados completos, consistentes e semanticamente enriquecidos.