# 03. Organização

## Objetivo

Esta seção define a organização arquitetural do Developer Portal dentro da Deja Platform.

O objetivo é estabelecer a separação de responsabilidades, os principais domínios internos da capacidade e sua relação com os demais componentes institucionais.

---

## Visão organizacional

O Developer Portal é organizado como uma capacidade transversal da plataforma.

Sua estrutura interna é composta por áreas responsáveis por:

- experiência do consumidor;
- catálogo de APIs;
- documentação;
- gestão de consumidores;
- integração com governança;
- operação do portal.

Modelo conceitual:

```text
Developer Portal
|
+-- Consumer Experience
|
+-- API Catalog
|
+-- Documentation Experience
|
+-- Consumer Management
|
+-- Integration Layer
|
+-- Portal Operations