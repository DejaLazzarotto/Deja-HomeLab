# 01. Visão Geral

## Objetivo

Esta seção apresenta a visão geral do Developer Portal dentro da arquitetura institucional da Deja Platform.

O Developer Portal representa a camada oficial de experiência, descoberta e integração dos consumidores das APIs disponibilizadas pela plataforma.

Seu propósito é transformar APIs em recursos compreensíveis, documentados e acessíveis para consumidores autorizados, mantendo governança, segurança e rastreabilidade.

---

## Contexto arquitetural

A Deja Platform possui diversas capacidades internas expostas através de APIs.

Com a evolução da plataforma, torna-se necessário estabelecer uma camada responsável por organizar a relação entre:

- APIs disponíveis;
- consumidores;
- documentação;
- contratos;
- processos de acesso;
- experiências de integração.

O Developer Portal surge como resposta a essa necessidade.

---

## Papel institucional

O Developer Portal é responsável por fornecer o ponto oficial de contato entre consumidores e o ecossistema de APIs da Deja Platform.

Ele permite que consumidores:

- conheçam capacidades disponíveis;
- compreendam contratos de integração;
- consultem documentação;
- solicitem acesso;
- acompanhem recursos autorizados.

---

## Posicionamento na arquitetura

O Developer Portal está posicionado na camada de experiência e consumo.

Modelo:

```text
+--------------------------------+
|        Consumidores            |
+--------------------------------+
                |
                v
+--------------------------------+
|       Developer Portal         |
+--------------------------------+
                |
                v
+--------------------------------+
|       API Management           |
+--------------------------------+
                |
                v
+--------------------------------+
|        API Gateway             |
+--------------------------------+
                |
                v
+--------------------------------+
| Runtime / Services             |
+--------------------------------+