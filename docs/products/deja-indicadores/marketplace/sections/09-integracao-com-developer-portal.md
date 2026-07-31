# 9. Integração com Developer Portal

## Objetivo

Esta seção define a integração arquitetural entre o Marketplace e o Developer Portal da Deja Platform.

O objetivo é estabelecer como capacidades publicadas no Marketplace podem ser descobertas, apresentadas e consumidas através da experiência institucional fornecida pelo Developer Portal.

---

## Visão geral

O Marketplace e o Developer Portal possuem responsabilidades complementares.

O Marketplace é responsável por:

- catálogo de capacidades;
- publicação;
- distribuição;
- governança do ecossistema.

O Developer Portal é responsável por:

- experiência dos consumidores;
- descoberta;
- documentação;
- interação com capacidades disponíveis.

---

## Princípio de integração

O Developer Portal não substitui o Marketplace.

A separação permanece:
Marketplace

Responsável por:

produtos;
módulos;
extensões;
publicação;
distribuição.

Developer Portal

Responsável por:

experiência;
documentação;
descoberta;
integração.


---

## Fluxo conceitual

O fluxo de integração segue:
Marketplace Catalog

    |
    v

Developer Portal

    |
    v

Consumer Discovery

    |
    v

Access Request

    |
    v

Marketplace Process


---

## Catálogo de capacidades

O Developer Portal pode consumir informações disponibilizadas pelo Marketplace.

Essas informações incluem:

- nome da capacidade;
- descrição;
- categoria;
- produtor;
- versões;
- documentação;
- disponibilidade.

---

## Fonte institucional

O Marketplace permanece como fonte institucional das informações relacionadas ao ecossistema.

O Developer Portal apresenta essas informações aos consumidores.

---

## Documentação associada

Capacidades publicadas no Marketplace devem possuir documentação associada.

O Developer Portal pode disponibilizar:

- descrição funcional;
- documentação técnica;
- guias de utilização;
- exemplos;
- requisitos;
- notas de versão.

---

## Descoberta de capacidades

A integração permite que consumidores encontrem:

- módulos;
- extensões;
- soluções;
- integrações;
- capacidades disponíveis.

---

## Solicitação de acesso

Quando um consumidor deseja utilizar uma capacidade, o Developer Portal pode iniciar o fluxo de solicitação.

O processamento permanece sob responsabilidade do Marketplace integrado com:

- Security;
- Administration Platform;
- Billing/Licensing quando aplicável.

---

## Versionamento

O Developer Portal deve apresentar as versões publicadas pelo Marketplace.

Devem ser mantidas informações sobre:

- versão atual;
- versões anteriores;
- compatibilidade;
- status de suporte.

---

## Segurança

O acesso às capacidades deve respeitar os mecanismos institucionais de Security.

Security permanece responsável por:

- identidade;
- autenticação;
- autorização;
- permissões.

---

## Observabilidade

As interações entre Developer Portal e Marketplace devem gerar informações operacionais.

Exemplos:

- visualizações;
- consultas;
- solicitações;
- acessos;
- conversões de consumo.

Integração:

- Observability;
- Execution Log.

---

## Rastreabilidade

Eventos relevantes da integração devem ser registrados.

Exemplos:

- publicação disponibilizada;
- catálogo sincronizado;
- documentação atualizada;
- solicitação iniciada;
- acesso concedido.

Integrações:

- Execution Log;
- Execution History.

---

## Governança

A integração deve preservar:

- fonte oficial dos dados;
- separação de responsabilidades;
- versionamento;
- rastreabilidade;
- segurança.

---

## Evolução futura

A integração poderá suportar:

- experiências personalizadas;
- recomendações de capacidades;
- onboarding automatizado;
- documentação dinâmica;
- integração com parceiros.

---

## Resultado esperado

A integração entre Marketplace e Developer Portal estabelece uma experiência consistente para descoberta e consumo de capacidades, mantendo governança, rastreabilidade e separação arquitetural entre ecossistema e experiência do consumidor.