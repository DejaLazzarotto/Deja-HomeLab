# 05. Componentes

## Objetivo

Esta seção descreve os componentes que compõem a arquitetura interna do Decision Engine.

Cada componente possui responsabilidade única e interfaces bem definidas, preservando a separação de responsabilidades, a reutilização e a evolução independente da implementação.

---

## Visão geral

A arquitetura do Decision Engine é composta pelos seguintes componentes:

```text
Decision Engine
│
├── Decision Definition Registry
├── Decision Policy Registry
├── Decision Rule Registry
├── Decision Criteria Registry
├── Decision Constraint Registry
├── Decision Context Builder
├── Decision Evaluator
├── Alternative Analyzer
├── Decision Prioritizer
├── Decision Confidence Evaluator
├── Decision Trace Builder
├── Decision Instance Builder
└── Decision Repository
```

Cada componente representa um serviço institucional do processo decisório.

---

## Decision Definition Registry

Responsável pelo gerenciamento das **Decision Definitions**.

Suas responsabilidades incluem:

- registrar definições de decisão;
- recuperar definições vigentes;
- controlar versões;
- disponibilizar definições para o processo decisório.

---

## Decision Policy Registry

Gerencia todas as políticas utilizadas durante a tomada de decisão.

É responsável por:

- registrar políticas;
- controlar versões;
- disponibilizar políticas ativas;
- manter governança das políticas institucionais.

---

## Decision Rule Registry

Centraliza as regras utilizadas durante a avaliação das alternativas.

Suas responsabilidades incluem:

- registrar regras;
- organizar regras por domínio;
- disponibilizar regras para avaliação;
- manter rastreabilidade das regras aplicadas.

---

## Decision Criteria Registry

Responsável pelo catálogo institucional de critérios de decisão.

Cada critério possui:

- identificação;
- descrição;
- forma de avaliação;
- regras de utilização;
- versionamento.

---

## Decision Constraint Registry

Gerencia todas as restrições consideradas pelo processo decisório.

Entre elas:

- financeiras;
- operacionais;
- estratégicas;
- regulatórias;
- legais;
- técnicas.

---

## Decision Context Builder

Responsável pela construção do contexto completo da decisão.

O contexto consolida:

- indicadores;
- diagnósticos;
- recomendações;
- conhecimento institucional;
- políticas;
- critérios;
- restrições;
- informações adicionais.

Esse componente produz uma visão única utilizada durante toda a avaliação.

---

## Decision Evaluator

Representa o núcleo lógico do Decision Engine.

Suas responsabilidades incluem:

- interpretar o contexto;
- aplicar políticas;
- validar restrições;
- avaliar critérios;
- selecionar alternativas elegíveis;
- consolidar a decisão.

O Decision Evaluator não executa ações operacionais.

---

## Alternative Analyzer

Responsável pela análise comparativa das alternativas disponíveis.

Para cada alternativa podem ser avaliados:

- benefícios;
- riscos;
- impacto esperado;
- aderência aos critérios;
- compatibilidade com políticas;
- conformidade com restrições.

---

## Decision Prioritizer

Determina a prioridade institucional da decisão.

Pode considerar fatores como:

- criticidade;
- urgência;
- impacto organizacional;
- risco;
- oportunidade;
- valor esperado.

A classificação segue padrões definidos pela governança.

---

## Decision Confidence Evaluator

Calcula o nível de confiança associado à decisão produzida.

A avaliação pode considerar:

- qualidade dos dados;
- completude do contexto;
- consistência dos diagnósticos;
- robustez das recomendações;
- aderência aos critérios;
- quantidade de evidências disponíveis.

O nível de confiança auxilia a interpretação da decisão, sem alterar seu conteúdo.

---

## Decision Trace Builder

Responsável pela construção da rastreabilidade completa da decisão.

Deve registrar os vínculos entre:

- indicadores;
- diagnósticos;
- recomendações;
- políticas;
- regras;
- critérios;
- restrições;
- itens da Knowledge Base;
- decisão produzida.

Esse componente garante auditabilidade integral.

---

## Decision Instance Builder

Responsável pela criação da **Decision Instance**, que representa o registro oficial de uma decisão.

Cada instância deverá conter:

- identificador único;
- definição utilizada;
- contexto;
- alternativa selecionada;
- justificativa;
- prioridade;
- nível de confiança;
- resultado;
- rastreabilidade;
- versão.

---

## Decision Repository

Responsável pelo armazenamento institucional das decisões produzidas.

Suas responsabilidades incluem:

- persistência;
- consulta;
- versionamento;
- histórico;
- auditoria;
- recuperação.

O repositório representa a fonte oficial das decisões corporativas da Deja Indicadores.

---

## Organização arquitetural

Os componentes apresentados nesta seção formam uma arquitetura modular, extensível e independente da tecnologia utilizada.

Cada componente poderá evoluir individualmente, desde que mantenha seus contratos institucionais e preserve a rastreabilidade, a governança e a consistência do processo decisório.