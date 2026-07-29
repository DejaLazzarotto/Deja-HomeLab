# Mapa de Capacidades — Deja Indicadores

## Visão Geral

O Mapa de Capacidades representa a decomposição institucional das capacidades de negócio da Deja Indicadores.

Seu propósito é organizar o conhecimento do produto em uma estrutura hierárquica que servirá como referência para a construção do Backlog de Valor, da Arquitetura Funcional e da implementação.

Esta etapa não descreve funcionalidades, casos de uso ou detalhes técnicos. Seu foco é identificar, organizar e relacionar as capacidades de negócio que compõem o produto.

---

## Objetivos

O Mapa de Capacidades tem como objetivos:

- decompor o produto em capacidades de negócio;
- estabelecer uma estrutura hierárquica única para o produto;
- definir a organização das responsabilidades do domínio;
- servir como origem institucional para o Backlog de Valor;
- garantir rastreabilidade entre estratégia, arquitetura e implementação.

---

## Papel no Processo de Desenvolvimento

O Mapa de Capacidades representa a transição entre a Arquitetura do Produto e a construção do Backlog de Valor.

```text
Discussão Estratégica
        ↓
Especificação Institucional
        ↓
Aprovação
        ↓
Arquitetura
        ↓
Mapa de Capacidades
        ↓
Backlog de Valor
        ↓
Arquitetura Funcional
        ↓
Especificação Funcional
        ↓
Implementação
        ↓
Validação
        ↓
Documentação Final
        ↓
Commit
```

---

## Estrutura da Documentação

```text
capability-map/

├── README.md
├── capability-map-v1.md
└── sections/
    └── 01-modelo-de-capacidades.md
```

---

## Documentos

### README.md

Apresenta os objetivos da fase, sua organização e sua relação com as demais etapas do desenvolvimento.

### capability-map-v1.md

Documento Mestre responsável por definir o modelo institucional de capacidades utilizado pela Deja Indicadores.

### 01-modelo-de-capacidades.md

Contém a árvore hierárquica completa das capacidades do produto.

Essa árvore constitui a principal referência para a construção do Backlog de Valor.

---

## Resultado Esperado

Ao final desta fase será possível derivar, de forma totalmente rastreável:

```text
Capacidade
        ↓
Subcapacidade
        ↓
Serviço de Negócio
        ↓
Backlog de Valor
        ↓
Arquitetura Funcional
        ↓
Especificação Funcional
        ↓
Implementação
        ↓
Testes
        ↓
Documentação
```

O Mapa de Capacidades constitui o catálogo institucional do conhecimento da Deja Indicadores, estabelecendo a ligação entre a Arquitetura do Produto e o desenvolvimento funcional do sistema.