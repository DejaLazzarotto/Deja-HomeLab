# 04. Modelo de API

## Objetivo

Esta seção define o modelo arquitetural de APIs utilizado pelo API Gateway da Deja Platform.

O modelo estabelece como APIs são estruturadas, identificadas, publicadas, consumidas e evoluídas dentro da plataforma.

---

# Visão geral

O API Gateway utiliza um modelo baseado em contratos públicos.

Cada API representa uma capacidade formalmente publicada pela plataforma, contendo:

- identidade;
- definição;
- versão;
- permissões;
- políticas;
- documentação;
- rastreabilidade.

As APIs são tratadas como recursos institucionais governados.

---

# Conceito de API

Uma API representa um contrato de comunicação entre um consumidor e uma capacidade da plataforma.

Uma API define:

- quais operações estão disponíveis;
- quais dados são recebidos;
- quais dados são retornados;
- quais políticas são aplicadas;
- quais versões existem.

---

# API Contract

O contrato da API é o elemento central do modelo.

Cada contrato deve possuir:

- identificador único;
- nome;
- descrição;
- versão;
- operações disponíveis;
- esquemas de entrada;
- esquemas de saída;
- requisitos de segurança;
- políticas aplicáveis.

---

# Identidade da API

Toda API deve possuir uma identidade institucional.

Modelo conceitual:
