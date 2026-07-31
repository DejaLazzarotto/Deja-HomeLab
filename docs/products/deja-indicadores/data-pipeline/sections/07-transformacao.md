# 07. Transformação

## Objetivo

A Transformação é responsável por converter o **Validated Dataset** em um conjunto de dados compatível com o modelo institucional da Deja Indicadores.

Seu objetivo é eliminar diferenças estruturais entre as diversas fontes de dados, produzindo uma representação uniforme para as etapas posteriores do pipeline.

A Transformação preserva o significado das informações, alterando apenas sua representação técnica.

---

## Papel na Arquitetura

Após a aprovação na etapa de Validação, os dados são encaminhados para a Transformação.

```text
Validated Dataset
        │
        ▼
 Transformation
        │
        ▼
Transformed Dataset
```

O resultado é um conjunto de dados tecnicamente padronizado, porém ainda não normalizado.

---

## Responsabilidades

A Transformação possui as seguintes responsabilidades institucionais:

- converter estruturas de dados;
- reorganizar atributos;
- renomear campos;
- converter tipos;
- padronizar formatos intermediários;
- separar ou agrupar informações;
- eliminar dependências específicas da origem;
- produzir o Transformed Dataset.

---

## Escopo

A Transformação atua exclusivamente sobre aspectos estruturais e técnicos.

Inclui, por exemplo:

- alteração de nomes de atributos;
- conversão de tipos numéricos;
- conversão de datas;
- reorganização de objetos;
- transformação de listas;
- desmembramento de campos compostos;
- composição de novos campos derivados da estrutura original.

Não inclui:

- validações;
- regras de negócio;
- normalização semântica;
- enriquecimento;
- cálculo de indicadores.

---

## Estratégias de Transformação

O Data Pipeline poderá utilizar diferentes estratégias.

### Mapeamento Direto

Um atributo de origem corresponde diretamente a um atributo institucional.

Exemplo:

```text
client_name
        │
        ▼
customerName
```

---

### Reestruturação

Os dados são reorganizados para atender ao modelo institucional.

Exemplo:

```text
address.street
address.number
address.city
```

pode tornar-se:

```text
location
```

com estrutura padronizada.

---

### Conversão de Tipos

Conversão entre representações equivalentes.

Exemplos:

- texto para número;
- texto para data;
- inteiro para decimal;
- booleano;
- enumerações.

---

### Composição

Dois ou mais atributos podem originar um novo atributo institucional.

Exemplo:

```text
firstName
lastName
```

↓

```text
fullName
```

---

### Decomposição

Um atributo poderá ser dividido em diversos campos institucionais.

Exemplo:

```text
"12345-678"
```

↓

```text
CEP
Complemento
```

quando aplicável.

---

## Regras de Transformação

As transformações deverão ser declarativas, versionadas e rastreáveis.

Cada regra deverá possuir:

- identificador;
- versão;
- origem;
- destino;
- descrição;
- responsável;
- histórico.

---

## Integridade

A Transformação não poderá modificar o significado dos dados.

Toda alteração deverá preservar a equivalência semântica entre origem e destino.

Caso isso não seja possível, a operação deverá ser rejeitada.

---

## Metadados Produzidos

A etapa registra, no mínimo:

- Pipeline Execution ID;
- versão das regras;
- quantidade de registros transformados;
- quantidade de transformações executadas;
- duração;
- falhas ocorridas;
- versão do modelo institucional.

---

## Eventos

A Transformação poderá publicar eventos como:

- TransformationStarted;
- TransformationCompleted;
- TransformationFailed;
- DatasetTransformed;
- TransformationRuleApplied.

Os eventos são distribuídos pelo Event Bus institucional.

---

## Integração

A Transformação comunica-se com:

- Pipeline Runtime;
- Pipeline Context;
- Metadata Registry;
- Event Bus;
- Observability;
- Registry.

Seu resultado é o **Transformed Dataset**, que será encaminhado para a etapa de Normalização.

---

## Princípio Institucional

A Transformação constitui a etapa responsável por adaptar tecnicamente os dados ao modelo institucional da Deja Indicadores, preservando integralmente seu significado original e eliminando dependências estruturais das fontes de origem.

Toda conversão deverá ser reproduzível, versionada, observável e completamente rastreável.