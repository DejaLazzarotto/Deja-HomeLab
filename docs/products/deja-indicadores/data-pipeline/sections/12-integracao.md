# 12. Integração

## Objetivo

A Integração define como o Data Pipeline comunica-se com os demais componentes da Deja Indicadores, preservando desacoplamento arquitetural, contratos institucionais e evolução independente.

O Data Pipeline não implementa regras de negócio dos componentes consumidores, limitando-se a disponibilizar conjuntos de dados oficialmente publicados.

---

## Visão Geral

O Data Pipeline ocupa a posição de infraestrutura de preparação de dados dentro do ecossistema institucional.

```text
                External Sources
                       │
                       ▼
                Data Pipeline
                       │
                       ▼
              Intelligence Core
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
 Diagnostic      Decision      Recommendation
    Engine          Engine            Engine
        │              │              │
        └──────────────┼──────────────┘
                       ▼
              Dashboard Engine
```

Toda comunicação ocorre por meio de contratos públicos e componentes homologados.

---

## Integração com o Intelligence Core

O Intelligence Core representa o principal consumidor dos Datasets publicados.

Suas responsabilidades incluem:

- descoberta de Datasets disponíveis;
- coordenação da execução dos Engines;
- compartilhamento do Context;
- gerenciamento do Runtime;
- propagação de eventos institucionais.

O Data Pipeline não depende da implementação interna do Intelligence Core.

---

## Integração com o Indicator Catalog

O Indicator Catalog fornece informações institucionais utilizadas durante:

- normalização;
- enriquecimento;
- classificação;
- identificação de indicadores.

A integração ocorre exclusivamente por interfaces públicas.

---

## Integração com a Knowledge Base

A Knowledge Base fornece conhecimento reutilizável para:

- enriquecimento semântico;
- conceitos institucionais;
- terminologia;
- relacionamentos;
- metadados.

O Data Pipeline consulta a Knowledge Base sem alterar seu conteúdo.

---

## Integração com os Engines

Os Engines especializados consomem apenas **Published Datasets**.

Não existe acesso direto às etapas intermediárias do pipeline.

Os principais consumidores são:

- Diagnostic Engine;
- Decision Engine;
- Recommendation Engine;
- Dashboard Engine.

Essa política garante isolamento entre infraestrutura e lógica de negócio.

---

## Integração com Fontes Externas

A comunicação com sistemas externos ocorre exclusivamente por meio dos **Source Connectors**.

Exemplos de integrações:

- bancos de dados;
- APIs REST;
- GraphQL;
- arquivos estruturados;
- ERPs;
- CRMs;
- serviços corporativos;
- provedores de dados.

Novas integrações podem ser adicionadas sem alterações na arquitetura principal.

---

## Integração com o Event Bus

O Data Pipeline publica e consome eventos institucionais.

Eventos típicos incluem:

- início de execução;
- conclusão;
- falhas;
- publicação;
- versionamento;
- monitoramento.

Essa comunicação é totalmente desacoplada.

---

## Integração com o Registry

O Registry é responsável pela descoberta dinâmica de componentes como:

- Source Connectors;
- Validadores;
- Transformadores;
- Normalizadores;
- Enriquecedores;
- Publicadores;
- Observadores.

Novos componentes podem ser registrados sem modificar o Runtime.

---

## Integração com a Observability

Todas as etapas do pipeline produzem informações consumidas pela infraestrutura de Observability.

Incluem:

- métricas;
- logs;
- tracing;
- auditoria;
- eventos;
- indicadores operacionais.

---

## Contratos Públicos

Toda integração deverá utilizar exclusivamente contratos públicos definidos pela arquitetura institucional.

Esses contratos garantem:

- interoperabilidade;
- compatibilidade evolutiva;
- independência entre componentes;
- substituição transparente de implementações.

---

## Princípio Institucional

O Data Pipeline integra-se ao restante da Deja Indicadores exclusivamente por interfaces institucionais, contratos públicos e mecanismos de infraestrutura compartilhada.

Essa estratégia preserva o desacoplamento arquitetural, facilita a evolução independente dos componentes e assegura que toda a inteligência da plataforma opere sobre conjuntos de dados oficialmente preparados e publicados.