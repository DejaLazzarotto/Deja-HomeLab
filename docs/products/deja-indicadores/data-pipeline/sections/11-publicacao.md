# 11. Publicação

## Objetivo

A Publicação é responsável por disponibilizar oficialmente os conjuntos de dados produzidos pelo Data Pipeline para consumo pelo Intelligence Core e pelos demais componentes da Deja Indicadores.

Somente Datasets aprovados, enriquecidos e versionados poderão ser publicados.

A Publicação representa o encerramento formal do ciclo de preparação dos dados.

---

## Papel na Arquitetura

A Publicação sucede o Versionamento.

```text
Versioned Dataset
        │
        ▼
   Publication
        │
        ▼
 Published Dataset
        │
        ▼
 Intelligence Core
        │
        ▼
 Specialized Engines
```

Após esta etapa, o Dataset passa a fazer parte do catálogo oficial de dados disponíveis para a plataforma.

---

## Responsabilidades

A Publicação possui as seguintes responsabilidades:

- disponibilizar o Dataset oficialmente;
- registrar a publicação;
- controlar o estado do Dataset;
- atualizar os metadados institucionais;
- comunicar a disponibilidade aos componentes consumidores;
- preservar a imutabilidade da versão publicada.

---

## Estados do Dataset

Durante seu ciclo de vida, um Dataset poderá assumir os seguintes estados:

```text
Raw
    │
    ▼
Validated
    │
    ▼
Transformed
    │
    ▼
Normalized
    │
    ▼
Enriched
    │
    ▼
Versioned
    │
    ▼
Published
```

Somente o estado **Published** autoriza o consumo institucional.

---

## Critérios de Publicação

Antes da publicação deverão ser verificados, no mínimo:

- validação concluída com sucesso;
- transformação concluída;
- normalização concluída;
- enriquecimento concluído;
- versionamento concluído;
- metadados obrigatórios disponíveis;
- rastreabilidade preservada.

Caso qualquer requisito não seja atendido, a publicação deverá ser rejeitada.

---

## Registro da Publicação

Cada publicação deverá registrar:

- Dataset ID;
- versão;
- Pipeline Execution ID;
- data e hora;
- responsável pela execução;
- política de publicação utilizada;
- hash da versão publicada;
- status final.

Essas informações tornam-se permanentes.

---

## Disponibilização

Após a publicação, o Dataset poderá ser consumido por:

- Intelligence Core;
- Indicator Catalog;
- Diagnostic Engine;
- Decision Engine;
- Recommendation Engine;
- Dashboard Engine;
- APIs institucionais;
- componentes autorizados.

O acesso ocorre exclusivamente por meio das interfaces oficiais da plataforma.

---

## Imutabilidade

Datasets publicados são imutáveis.

Caso seja necessária qualquer alteração, uma nova versão deverá ser produzida e publicada.

A versão anterior permanece disponível conforme a política institucional de retenção.

---

## Eventos

A Publicação poderá gerar eventos como:

- PublicationStarted;
- PublicationCompleted;
- PublicationFailed;
- DatasetPublished;
- DatasetAvailable;
- DatasetDeprecated.

Todos os eventos são distribuídos pelo Event Bus institucional.

---

## Metadados Produzidos

Ao término da Publicação deverão ser registrados:

- Dataset ID;
- versão publicada;
- timestamp da publicação;
- Pipeline Execution ID;
- estado final;
- componentes consumidores habilitados;
- evidências da publicação.

---

## Integração

A Publicação comunica-se com:

- Pipeline Runtime;
- Pipeline Context;
- Metadata Registry;
- Registry;
- Event Bus;
- Observability;
- Intelligence Core.

A partir desta etapa, o Dataset deixa de pertencer exclusivamente ao Data Pipeline e passa a integrar o ecossistema oficial de dados da Deja Indicadores.

---

## Princípio Institucional

A Publicação constitui o único mecanismo autorizado para disponibilização de dados ao ecossistema da Deja Indicadores.

Nenhum componente poderá consumir conjuntos de dados que não tenham sido oficialmente publicados pelo Data Pipeline.

Esse princípio garante consistência, rastreabilidade, reprodutibilidade e governança sobre todas as informações utilizadas pela plataforma.