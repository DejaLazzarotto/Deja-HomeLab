# 06 — Modelo de Dados

## Objetivo

Este documento define o Modelo de Dados da Deja Indicadores.

Seu objetivo é estabelecer a organização lógica das informações persistidas pelo produto, preservando a independência em relação às tecnologias de armazenamento e aos mecanismos concretos de persistência.

O Modelo de Dados traduz os conceitos do Modelo de Domínio em estruturas lógicas de informação, mantendo rastreabilidade com a Arquitetura Funcional e com os Agregados de Domínio.

---

# Princípios

O Modelo de Dados deve observar os seguintes princípios:

- independência tecnológica;
- consistência com o Modelo de Domínio;
- normalização lógica quando aplicável;
- integridade das informações;
- rastreabilidade funcional;
- extensibilidade.

---

# Organização

Os dados do produto estão organizados em conjuntos lógicos correspondentes aos principais agregados do domínio.

| Conjunto de Dados | Agregado Relacionado |
|-------------------|----------------------|
| Indicadores | Indicador |
| Catálogo | Catálogo de Indicadores |
| Consultas | Consulta |
| Favoritos | Favoritos |
| Histórico | Histórico |

Outros conjuntos poderão ser incorporados conforme a evolução do produto.

---

# Estruturas Lógicas

## Indicadores

Armazena as informações essenciais de cada indicador.

Exemplos de atributos:

- identificador;
- código;
- nome;
- descrição;
- categoria;
- órgão responsável;
- unidade de medida;
- periodicidade;
- situação;
- data da última atualização.

---

## Catálogo

Representa a organização lógica dos indicadores disponibilizados ao usuário.

Exemplos de atributos:

- identificador;
- indicador relacionado;
- categoria;
- posição lógica;
- disponibilidade.

---

## Consultas

Representa as consultas realizadas pelos usuários.

Exemplos de atributos:

- identificador;
- usuário;
- critérios utilizados;
- data e hora;
- quantidade de resultados.

---

## Favoritos

Representa os indicadores marcados como favoritos por cada usuário.

Exemplos de atributos:

- identificador;
- usuário;
- indicador;
- data de inclusão.

---

## Histórico

Representa o histórico funcional de utilização do catálogo.

Exemplos de atributos:

- identificador;
- usuário;
- indicador;
- data e hora da consulta;
- origem da consulta.

---

# Relacionamentos Lógicos

Os conjuntos de dados relacionam-se de forma consistente com os agregados de domínio.

Exemplos:

- um Catálogo contém diversos Indicadores;
- um Usuário pode possuir diversos Favoritos;
- um Usuário pode possuir diversas Consultas;
- uma Consulta pode referenciar diversos Indicadores;
- um Histórico registra consultas realizadas.

Os mecanismos concretos de relacionamento serão definidos na implementação.

---

# Integridade

O Modelo de Dados deve garantir:

- unicidade dos identificadores;
- consistência dos relacionamentos;
- preservação das regras definidas no domínio;
- integridade referencial lógica.

---

# Persistência

A Arquitetura Técnica não impõe uma tecnologia específica de persistência.

A implementação poderá utilizar diferentes mecanismos, desde que preservem:

- os contratos do domínio;
- a consistência dos dados;
- a rastreabilidade funcional.

---

# Evolução

O Modelo de Dados deverá evoluir de forma compatível com:

- o Modelo de Domínio;
- a Arquitetura Funcional;
- as Functional Specifications;
- os princípios arquiteturais.

Alterações incompatíveis deverão ser tratadas por mecanismos de versionamento e migração.

---

# Rastreabilidade

```
Capability
        ↓
Epic
        ↓
Functional Module
        ↓
Feature
        ↓
Functional Specification
        ↓
Modelo de Domínio
        ↓
Modelo de Dados
        ↓
Persistência
        ↓
Código
```

---

# Governança

Toda alteração no Modelo de Dados deve:

- preservar compatibilidade com o Modelo de Domínio;
- manter rastreabilidade funcional;
- evitar dependências tecnológicas;
- ser documentada antes da implementação.

---

# Conclusão

O Modelo de Dados estabelece a organização lógica das informações da Deja Indicadores, fornecendo uma base consistente para a implementação da persistência e para a evolução futura do produto, sem comprometer a independência arquitetural ou tecnológica.