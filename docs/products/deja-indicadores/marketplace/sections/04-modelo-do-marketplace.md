# 4. Modelo do Marketplace

## Objetivo

Esta seção define o modelo conceitual do Marketplace da Deja Platform.

O modelo estabelece as principais entidades, relacionamentos e fluxos necessários para representar capacidades distribuíveis dentro do ecossistema.

---

## Visão geral do modelo

O Marketplace organiza capacidades através de um conjunto de entidades institucionais.

Modelo conceitual:
# 4. Modelo do Marketplace

## Objetivo

Esta seção define o modelo conceitual do Marketplace da Deja Platform.

O modelo estabelece as principais entidades, relacionamentos e fluxos necessários para representar capacidades distribuíveis dentro do ecossistema.

---

## Visão geral do modelo

O Marketplace organiza capacidades através de um conjunto de entidades institucionais.

Modelo conceitual:
Producer
|
v
Product
|
+--> Module
|
+--> Extension
|
+--> Package
|
+--> Version
|
v
Marketplace Listing
|
v
Consumer

---

# Producer

Representa a entidade responsável pela criação e publicação de capacidades.

Um Producer pode ser:

- equipe interna;
- unidade organizacional;
- parceiro;
- fornecedor externo.

Responsabilidades:

- manter propriedade da capacidade;
- fornecer documentação;
- publicar versões;
- responder pela evolução.

---

# Product

Representa uma capacidade disponibilizada no Marketplace.

Um Product agrega informações de negócio e apresentação.

Exemplos:

- solução;
- módulo funcional;
- extensão;
- pacote de capacidades.

Principais atributos:

- identificação;
- nome;
- descrição;
- categoria;
- proprietário;
- status;
- versões disponíveis.

---

# Module

Representa uma unidade técnica instalável da Deja Platform.

O Marketplace utiliza informações técnicas provenientes da Module Platform e Module Registry.

Responsabilidades mantidas:

- definição técnica;
- ciclo de vida interno;
- contratos;
- dependências.

---

# Extension

Representa uma extensão capaz de ampliar funcionalidades existentes.

Exemplos:

- componentes adicionais;
- integrações;
- provedores;
- recursos complementares.

---

# Package

Representa o artefato distribuível associado a uma capacidade.

Pode conter:

- código;
- configurações;
- recursos;
- metadados;
- dependências.

A distribuição física permanece sob responsabilidade do Package Distribution.

---

# Version

Representa uma versão específica publicada.

Toda versão deve possuir:

- identificação;
- compatibilidade;
- documentação;
- histórico;
- estado de publicação.

O versionamento é obrigatório.

---

# Marketplace Listing

Representa a publicação de uma capacidade dentro do Marketplace.

É a visão apresentada aos consumidores.

Pode conter:

- informações comerciais;
- documentação;
- imagens;
- requisitos;
- avaliações;
- disponibilidade.

---

# Consumer

Representa a entidade que descobre e utiliza capacidades publicadas.

Pode representar:

- organização;
- usuário autorizado;
- aplicação;
- ambiente.

Responsabilidades:

- solicitar acesso;
- instalar capacidades;
- acompanhar consumo.

---

## Estados de uma capacidade

Uma capacidade publicada pode possuir estados:
DRAFT
|
v
SUBMITTED
|
v
VALIDATED
|
v
APPROVED
|
v
PUBLISHED
|
v
DEPRECATED
|
v
REMOVED


---

## Relacionamento com registros técnicos

O Marketplace não substitui os registros técnicos internos.

Relacionamento:
Marketplace Product
|
v
Module Registry
|
v
Module Platform


O Marketplace mantém a representação de ecossistema enquanto os registros técnicos permanecem nas capacidades especializadas.

---

## Princípios do modelo

O modelo deve garantir:

- identidade única;
- rastreabilidade;
- versionamento;
- separação entre negócio e tecnologia;
- evolução independente;
- governança institucional.

---

## Resultado esperado

O modelo permite que a Deja Platform suporte um ecossistema organizado de capacidades distribuídas, mantendo controle técnico, governança e preparação para modelos comerciais futuros.