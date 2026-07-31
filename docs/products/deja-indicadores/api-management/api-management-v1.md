# API Management — Deja Platform v1

## 1. Introdução

O API Management estabelece a capacidade institucional responsável pelo gerenciamento completo do ciclo de vida das APIs da Deja Platform.

Esta capacidade transforma APIs em recursos arquiteturais governados, garantindo que sua criação, publicação, consumo, evolução e descontinuação ocorram de maneira controlada, rastreável e compatível com os princípios da plataforma.

O API Management complementa o API Gateway, fornecendo a camada de governança e operação das APIs.

Enquanto o API Gateway executa as chamadas em runtime, o API Management controla o ciclo de vida e as políticas associadas às APIs.

---

# 2. Objetivos

O API Management possui como objetivos principais:

- estabelecer um modelo institucional de gerenciamento de APIs;
- controlar o ciclo de vida completo das APIs;
- garantir padronização dos contratos públicos;
- permitir descoberta e consumo controlado;
- aplicar políticas de governança;
- manter histórico e rastreabilidade das alterações;
- fornecer métricas e indicadores de utilização;
- suportar evolução segura da plataforma.

---

# 3. Papel Arquitetural

O API Management representa a camada responsável pela administração das APIs dentro da arquitetura da Deja Platform.

Sua responsabilidade é garantir que uma API:

- possua identidade própria;
- tenha contrato definido;
- esteja registrada;
- possua proprietário responsável;
- tenha versões controladas;
- esteja submetida às políticas institucionais;
- tenha consumidores conhecidos;
- possua histórico operacional.

---

# 4. Relação com API Gateway

O API Management e o API Gateway possuem responsabilidades distintas.

## API Management

Responsável por:

- gestão;
- governança;
- catálogo;
- ciclo de vida;
- políticas;
- consumidores;
- métricas;
- aprovação.

## API Gateway

Responsável por:

- exposição;
- autenticação em runtime;
- autorização em runtime;
- roteamento;
- execução;
- aplicação das políticas publicadas.

Fluxo:
