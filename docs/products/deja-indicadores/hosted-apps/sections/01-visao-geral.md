# 01. Visão Geral

## Objetivo

A Hosted Apps estabelece a capacidade institucional responsável pela hospedagem, gerenciamento, isolamento, execução e operação das aplicações executadas na Deja Platform.

Seu propósito é disponibilizar um ambiente institucional padronizado para que aplicações possam ser implantadas e executadas de forma segura, escalável e integrada ao ecossistema da plataforma, independentemente de sua origem ou finalidade.

A Hosted Apps constitui exclusivamente uma infraestrutura de hospedagem e execução, não implementando funcionalidades de negócio das aplicações hospedadas.

---

## Papel Institucional

A Hosted Apps atua como a camada oficial de execução de aplicações da Deja Platform.

Compete a esta capacidade:

- registrar aplicações hospedadas
- disponibilizar ambientes de execução
- controlar o ciclo de vida das aplicações
- gerenciar deployment institucional
- garantir isolamento entre aplicações
- integrar aplicações às capacidades institucionais
- administrar versões implantadas
- controlar disponibilidade operacional
- fornecer infraestrutura de execução
- suportar evolução contínua da plataforma

---

## Escopo

A Hosted Apps é responsável por:

- hospedagem institucional
- deployment
- inicialização
- parada
- atualização
- rollback
- gerenciamento operacional
- isolamento
- versionamento
- execução
- monitoramento operacional
- integração institucional

Não fazem parte do seu escopo:

- desenvolvimento das aplicações
- implementação de regras de negócio
- experiência do usuário das aplicações
- interfaces específicas
- lógica funcional dos domínios

---

## Aplicações Hospedadas

A arquitetura suporta diferentes categorias de aplicações:

- aplicações institucionais da Deja Platform
- aplicações comerciais
- aplicações desenvolvidas por clientes
- aplicações corporativas
- aplicações de parceiros
- aplicações de terceiros homologadas

Todas seguem o mesmo modelo institucional de hospedagem.

---

## Objetivos Arquiteturais

A Hosted Apps foi concebida para garantir:

- isolamento entre aplicações
- segurança operacional
- escalabilidade horizontal
- gerenciamento centralizado
- deployment padronizado
- observabilidade completa
- rastreabilidade integral
- integração com capacidades institucionais
- alta disponibilidade
- evolução contínua

---

## Princípios Gerais

A arquitetura da Hosted Apps adota os seguintes princípios:

- hospedagem desacoplada do domínio de negócio
- execução baseada em contratos públicos
- isolamento por tenant e aplicação
- gerenciamento centralizado
- integração institucional obrigatória
- observabilidade nativa
- segurança por padrão
- evolução compatível com a arquitetura institucional da Deja Platform