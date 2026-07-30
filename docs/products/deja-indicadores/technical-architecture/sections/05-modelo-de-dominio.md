# 05 — Modelo de Domínio

## Objetivo

Este documento define o Modelo de Domínio da Deja Indicadores.

O Modelo de Domínio representa os conceitos centrais do negócio, suas responsabilidades, relacionamentos e regras conceituais, servindo como referência para a implementação técnica do produto.

Este documento permanece independente da tecnologia utilizada, do mecanismo de persistência e da arquitetura de implantação.

---

# Visão Geral

A Deja Indicadores adota um modelo orientado ao domínio, organizado em Contextos de Domínio e Agregados de Domínio.

Cada agregado representa uma unidade consistente de negócio, responsável por proteger suas invariantes e garantir a integridade das operações realizadas sobre seus dados.

---

# Contextos de Domínio

O domínio da Deja Indicadores está organizado nos seguintes contextos:

| Contexto | Responsabilidade |
|----------|------------------|
| Catálogo | Disponibilização e organização dos indicadores. |
| Consulta | Pesquisa, filtragem, ordenação e navegação. |
| Visualização | Apresentação dos indicadores ao usuário. |
| Compartilhamento | Compartilhamento e exportação de indicadores. |
| Preferências | Favoritos, histórico e preferências do usuário. |

Novos contextos poderão ser incorporados conforme a evolução do produto.

---

# Agregados de Domínio

## Indicador

Representa a unidade central do domínio.

É responsável por manter todas as informações relacionadas a um indicador e garantir sua consistência funcional.

### Responsabilidades

- identidade do indicador;
- informações descritivas;
- metadados;
- situação;
- regras de disponibilidade.

---

## Catálogo de Indicadores

Representa o conjunto organizado de indicadores disponíveis para consulta.

### Responsabilidades

- disponibilização dos indicadores;
- navegação;
- organização lógica do catálogo.

---

## Consulta

Representa uma sessão de consulta realizada pelo usuário.

### Responsabilidades

- critérios utilizados;
- contexto da consulta;
- resultados obtidos.

---

## Favoritos

Representa a coleção de indicadores marcada pelo usuário.

### Responsabilidades

- inclusão;
- remoção;
- consulta da coleção.

---

## Histórico

Representa o histórico funcional das consultas realizadas pelo usuário.

### Responsabilidades

- registro;
- recuperação;
- limpeza.

---

# Entidades

As principais entidades do domínio incluem:

- Indicador;
- Categoria;
- Órgão Responsável;
- Fonte de Dados;
- Usuário (referência funcional).

Outras entidades poderão ser incorporadas conforme a evolução do produto.

---

# Objetos de Valor

Exemplos de Objetos de Valor utilizados no domínio:

- Identificador do Indicador;
- Código do Indicador;
- Período;
- Unidade de Medida;
- Intervalo de Datas;
- Critério de Pesquisa;
- Critério de Ordenação;
- Critério de Filtragem.

Objetos de Valor são definidos por seus atributos e não por identidade própria.

---

# Serviços de Domínio

Os Serviços de Domínio concentram operações que não pertencem naturalmente a um único agregado.

Exemplos:

- Pesquisa de Indicadores;
- Aplicação de Filtros;
- Ordenação de Resultados;
- Exportação;
- Compartilhamento.

---

# Eventos de Domínio

O domínio poderá publicar eventos representando alterações relevantes de estado.

Exemplos:

- Indicador Consultado;
- Favorito Adicionado;
- Favorito Removido;
- Exportação Solicitada;
- Compartilhamento Realizado.

A definição detalhada dos eventos será documentada conforme a evolução do produto.

---

# Repositórios

Cada agregado poderá possuir um Repositório responsável pela persistência de seus dados.

Os Repositórios representam contratos do domínio e não implementações concretas.

Exemplos:

- Repositório de Indicadores;
- Repositório de Favoritos;
- Repositório de Histórico.

---

# Relações entre Agregados

Os agregados colaboram entre si preservando baixo acoplamento e alta coesão.

Nenhum agregado deve acessar diretamente o estado interno de outro agregado.

A comunicação entre agregados deve ocorrer por meio de contratos públicos ou eventos de domínio.

---

# Rastreabilidade

O Modelo de Domínio mantém correspondência direta com a arquitetura funcional.

```
Capability
        ↓
Epic
        ↓
Functional Module
        ↓
Feature
        ↓
Functional Function
        ↓
Functional Specification
        ↓
Agregado de Domínio
        ↓
Serviços de Domínio
        ↓
Código
```

---

# Evolução

Novos Contextos, Agregados, Entidades, Objetos de Valor e Serviços de Domínio poderão ser adicionados desde que:

- preservem a consistência do domínio;
- respeitem os limites dos contextos;
- mantenham responsabilidade única;
- garantam rastreabilidade funcional.

---

# Governança

Toda alteração no Modelo de Domínio deverá:

- manter compatibilidade com a Arquitetura Funcional;
- preservar os princípios arquiteturais;
- evitar dependências tecnológicas;
- atualizar a documentação correspondente.

---

# Conclusão

O Modelo de Domínio representa a visão conceitual oficial da Deja Indicadores.

Ele constitui a base para a implementação técnica do produto e estabelece a estrutura semântica sobre a qual serão construídos os serviços, APIs, persistência e demais componentes arquiteturais.