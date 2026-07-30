# Catálogo Oficial de Indicadores

Versão: 1.0

---

# Objetivo

Este documento estabelece a organização institucional do Catálogo Oficial de Indicadores da Deja Indicadores.

Seu propósito é definir os princípios, a estrutura documental e as diretrizes que orientam a especificação de todos os indicadores suportados pelo produto, garantindo consistência funcional, padronização técnica e rastreabilidade completa durante todo o ciclo de vida da solução.

Este documento não descreve indicadores específicos. Sua finalidade é estabelecer o modelo oficial utilizado para documentá-los.

---

# Escopo

O Catálogo Oficial de Indicadores aplica-se a todos os indicadores disponibilizados pela Deja Indicadores, independentemente do módulo funcional, da origem dos dados ou da forma de visualização.

Todos os indicadores deverão seguir obrigatoriamente os padrões definidos nesta documentação.

---

# Organização da Documentação

O Catálogo de Indicadores está organizado da seguinte forma:

```text
indicator-catalog/

├── README.md
├── indicator-catalog-v1.md
├── indicators/
├── shared/
└── sections/
```

Cada componente possui responsabilidade específica:

- **README.md** apresenta a visão geral do catálogo;
- **indicator-catalog-v1.md** estabelece as diretrizes institucionais;
- **sections/** documenta os aspectos estruturais do catálogo;
- **shared/** reúne componentes reutilizáveis;
- **indicators/** contém a documentação individual de cada indicador.

---

# Estrutura do Documento

Este Documento Mestre é complementado pelos seguintes documentos especializados:

- 01-visao-geral.md
- 02-organizacao-do-catalogo.md
- 03-modelo-de-indicador.md
- 04-classificacao.md
- 05-fontes-de-dados.md
- 06-calculos.md
- 07-visualizacoes.md
- 08-rastreabilidade.md
- 09-governanca.md
- 10-evolucao.md

Cada seção aborda um aspecto específico da organização institucional do catálogo.

---

# Modelo Institucional

Cada indicador deverá possuir documentação própria contendo, no mínimo:

- identificação única;
- objetivo;
- descrição funcional;
- regras de negócio;
- fórmula de cálculo;
- parâmetros;
- filtros suportados;
- dimensões analíticas;
- origem dos dados;
- periodicidade;
- visualizações suportadas;
- rastreabilidade funcional;
- rastreabilidade técnica;
- requisitos de implementação;
- requisitos de testes;
- histórico de evolução.

Esse modelo assegura uniformidade entre todos os indicadores do produto.

---

# Governança

Toda inclusão, alteração ou descontinuação de indicadores deverá ser previamente documentada.

Nenhum indicador poderá ser implementado sem documentação correspondente aprovada.

As alterações deverão preservar:

- compatibilidade funcional;
- consistência técnica;
- rastreabilidade;
- versionamento documental;
- alinhamento com a Arquitetura Técnica;
- alinhamento com a Arquitetura de Implementação.

---

# Relação com as Demais Arquiteturas

O Catálogo Oficial de Indicadores complementa as seguintes documentações institucionais:

- Product Vision;
- Product Architecture;
- Capability Map;
- Value Backlog;
- Functional Architecture;
- Functional Specifications;
- Technical Architecture;
- Implementation Architecture.

O catálogo representa a formalização dos artefatos analíticos implementados pelo produto.

---

# Rastreabilidade Institucional

A cadeia oficial permanece:

```text
CAP
 ↓
EP
 ↓
FM
 ↓
FE
 ↓
FF
 ↓
FS
 ↓
Arquitetura Técnica
 ↓
Arquitetura de Implementação
 ↓
Indicador
 ↓
Código
 ↓
Testes
 ↓
Documentação
```

Todo indicador deverá manter vínculo explícito com sua origem funcional e técnica.

---

# Evolução

Esta documentação deverá evoluir continuamente à medida que novos indicadores forem incorporados ao produto.

A estrutura institucional aqui definida permanece estável, permitindo a expansão do catálogo sem comprometer sua organização, governança e rastreabilidade.