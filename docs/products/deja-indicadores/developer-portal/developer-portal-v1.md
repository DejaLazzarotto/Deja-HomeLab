# Developer Portal — Arquitetura Institucional v1

## 1. Introdução

O Developer Portal estabelece a camada institucional de interação entre a Deja Platform e seus consumidores de APIs.

Sua responsabilidade é disponibilizar uma experiência controlada para descoberta, entendimento, solicitação de acesso e utilização dos recursos expostos pela plataforma.

O Developer Portal não executa APIs e não substitui o API Gateway ou o API Management.

Ele atua como camada de experiência e relacionamento com consumidores, consumindo informações provenientes das capacidades internas da plataforma.

---

## 2. Objetivo arquitetural

O objetivo do Developer Portal é criar um ponto oficial para:

- descoberta de APIs disponíveis;
- acesso à documentação técnica;
- compreensão dos contratos de integração;
- gerenciamento da jornada de consumidores;
- suporte ao processo de adoção das APIs;
- comunicação das capacidades disponíveis.

A arquitetura busca transformar APIs em produtos consumíveis e governados.

---

## 3. Posicionamento na arquitetura

O Developer Portal ocupa a camada de experiência de consumo da Deja Platform.

Modelo conceitual:

```text
                 Consumidores
                      |
                      v
             Developer Portal
                      |
        +-------------+-------------+
        |                           |
        v                           v
 API Management              API Registry
        |                           |
        v                           v
 API Gateway ---------------- Runtime
        |
        v
     Services