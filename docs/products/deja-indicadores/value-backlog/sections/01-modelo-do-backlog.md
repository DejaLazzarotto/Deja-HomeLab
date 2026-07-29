# Modelo do Backlog de Valor

## Objetivo

O Modelo do Backlog de Valor define a estrutura institucional utilizada para organizar a evolução funcional da Deja Indicadores.

Seu objetivo é garantir que todas as entregas do produto sejam planejadas de forma consistente, rastreável e alinhada às capacidades de negócio.

O modelo estabelece uma hierarquia única para todo o produto, evitando diferentes interpretações sobre o planejamento das funcionalidades.

---

## Estrutura Hierárquica

O Backlog de Valor é organizado segundo a seguinte hierarquia:

```text
Produto
        ↓
Épico
        ↓
Feature
        ↓
História
```

Cada nível possui uma responsabilidade específica e representa um nível diferente de detalhamento.

---

## Produto

Representa a solução comercial entregue ao mercado.

Para esta documentação, o produto é:

```text
Deja Indicadores
```

Todo o Backlog de Valor pertence exclusivamente a este produto.

---

## Épico

Um Épico representa uma grande entrega de valor para o cliente.

Cada Épico agrupa funcionalidades relacionadas por um objetivo comum de negócio.

Os Épicos possuem longa duração e normalmente são implementados ao longo de várias versões do produto.

---

## Feature

Uma Feature representa uma funcionalidade identificável pelo usuário.

Cada Feature pertence a um único Épico e produz uma entrega de valor perceptível para o cliente.

Uma Feature pode ser implementada por meio de uma ou mais Histórias.

---

## História

Uma História representa a menor unidade de planejamento da implementação.

Cada História descreve uma necessidade específica do usuário que pode ser desenvolvida, testada e entregue de forma independente.

As Histórias constituem a base para a Arquitetura Funcional, para a Especificação Funcional e para a implementação.

---

## Relação com o Mapa de Capacidades

Todo Épico deve possuir origem em uma ou mais capacidades definidas no Mapa de Capacidades.

Essa relação garante que a evolução do produto permaneça alinhada aos objetivos de negócio previamente estabelecidos.

```text
Mapa de Capacidades
        ↓
Épico
        ↓
Feature
        ↓
História
```

---

## Rastreabilidade

Cada História deverá manter rastreabilidade completa com os artefatos produzidos durante o desenvolvimento.

```text
Capacidade
        ↓
Épico
        ↓
Feature
        ↓
História
        ↓
Arquitetura Funcional
        ↓
Especificação Funcional
        ↓
Código
        ↓
Testes
        ↓
Documentação
```

---

## Evolução

O Modelo do Backlog permanece estável durante todo o ciclo de vida da Deja Indicadores.

Novos Épicos, Features e Histórias poderão ser adicionados conforme a evolução do produto, sem alterar a estrutura hierárquica definida neste documento.