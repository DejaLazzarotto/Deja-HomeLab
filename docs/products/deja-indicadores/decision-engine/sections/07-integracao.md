# 07. Integração

## Objetivo

Esta seção descreve a integração do Decision Engine com os demais componentes da Deja Indicadores.

O Decision Engine ocupa a camada de consolidação das decisões corporativas, consumindo informações produzidas pelos componentes anteriores e disponibilizando decisões estruturadas para os componentes consumidores.

---

## Visão geral

O posicionamento arquitetural do Decision Engine é representado pelo fluxo abaixo:

```text
Knowledge Base
        │
        ▼
Indicator Catalog
        │
        ▼
Diagnostic Engine
        │
        ▼
Recommendation Engine
        │
        ▼
Decision Engine
        │
        ▼
AI Assistant
```

Cada componente mantém responsabilidades independentes e interfaces institucionais bem definidas.

---

## Integração com o Indicator Catalog

O Decision Engine não consome indicadores diretamente durante o processo normal de decisão.

Os indicadores são interpretados previamente pelo Diagnostic Engine.

Entretanto, as referências aos indicadores permanecem disponíveis por meio do contexto e da rastreabilidade da decisão.

Essa separação evita o acoplamento entre o processo decisório e o cálculo de indicadores.

---

## Integração com a Knowledge Base

A Knowledge Base fornece conhecimento institucional reutilizável que pode apoiar o processo decisório.

Entre os itens consultados podem existir:

- políticas corporativas;
- regras organizacionais;
- procedimentos;
- melhores práticas;
- normas internas;
- conhecimento especializado.

O Decision Engine permanece consumidor da Knowledge Base, sem alterar seu conteúdo.

---

## Integração com o Diagnostic Engine

O Diagnostic Engine representa a principal origem das evidências utilizadas na tomada de decisão.

Cada decisão poderá estar associada a um ou mais diagnósticos.

O Decision Engine não modifica diagnósticos nem interfere em sua geração.

Sua responsabilidade limita-se à utilização das informações produzidas pelo Diagnostic Engine.

---

## Integração com o Recommendation Engine

O Recommendation Engine fornece as alternativas previamente estruturadas que serão avaliadas durante o processo decisório.

O Decision Engine utiliza essas recomendações como insumo para:

- análise das alternativas;
- aplicação de políticas;
- validação das restrições;
- comparação por critérios;
- consolidação da decisão.

O Recommendation Engine permanece responsável pela geração das recomendações, enquanto o Decision Engine é responsável pela escolha institucional da alternativa mais adequada.

---

## Integração com o AI Assistant

O AI Assistant atua como consumidor das decisões produzidas pelo Decision Engine.

Entre suas responsabilidades estão:

- apresentar a decisão ao usuário;
- explicar a justificativa;
- responder dúvidas;
- detalhar critérios utilizados;
- contextualizar impactos;
- apoiar a compreensão da decisão.

O AI Assistant não altera nem substitui as decisões oficiais produzidas pelo Decision Engine.

---

## Integração com consumidores futuros

A arquitetura prevê a integração futura com outros componentes, tais como:

- mecanismos de automação;
- workflows corporativos;
- motores de execução;
- sistemas externos;
- serviços de monitoramento;
- plataformas de governança.

Todos esses consumidores deverão utilizar exclusivamente as Decision Instances oficiais.

---

## Contrato institucional

A integração entre componentes ocorre por meio de contratos institucionais claramente definidos.

Esses contratos garantem:

- independência entre componentes;
- reutilização;
- evolução controlada;
- versionamento;
- rastreabilidade;
- compatibilidade entre versões.

Nenhum componente deverá acessar diretamente estruturas internas de outro componente.

---

## Princípios de integração

Toda integração envolvendo o Decision Engine deverá respeitar os seguintes princípios:

- separação de responsabilidades;
- baixo acoplamento;
- alta coesão;
- contratos explícitos;
- rastreabilidade completa;
- governança institucional;
- independência tecnológica.

Esses princípios asseguram a evolução sustentável da arquitetura da Deja Indicadores.

---

## Papel no Núcleo de Inteligência

O Decision Engine representa a camada responsável pela consolidação das decisões corporativas.

Sua posição no Núcleo de Inteligência pode ser resumida da seguinte forma:

- **Indicator Catalog** organiza os indicadores.
- **Diagnostic Engine** interpreta os indicadores.
- **Recommendation Engine** propõe alternativas.
- **Decision Engine** seleciona e consolida a decisão institucional.
- **AI Assistant** comunica e explica a decisão aos usuários.

Essa separação preserva a clareza arquitetural, evita sobreposição de responsabilidades e garante um processo decisório consistente, auditável e evolutivo.