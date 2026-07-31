# 10. Integração com Module Platform

## Objetivo

Esta seção define a integração arquitetural entre o Marketplace e a Module Platform da Deja Platform.

O objetivo é estabelecer como capacidades técnicas desenvolvidas como módulos e extensões são registradas, disponibilizadas e governadas dentro do ecossistema de distribuição.

---

## Visão geral

A Module Platform é responsável pela infraestrutura técnica dos módulos da Deja Platform.

O Marketplace utiliza as informações técnicas fornecidas pela Module Platform para organizar, publicar e distribuir capacidades aos consumidores.

A separação de responsabilidades permanece:
Module Platform

Responsável por:

estrutura técnica dos módulos;
contratos;
ciclo de vida técnico;
dependências;
execução.

Marketplace

Responsável por:

catálogo;
publicação;
descoberta;
distribuição;
governança do ecossistema.


---

## Princípio de integração

O Marketplace não substitui a Module Platform.

A Module Platform permanece como autoridade técnica sobre módulos e extensões.

O Marketplace representa a camada institucional de disponibilização dessas capacidades.

---

## Fluxo conceitual
Module Development

    |
    v

Module Platform

    |
    v

Module Registry

    |
    v

Marketplace

    |
    v

Consumers


---

## Registro de capacidades

A Module Platform fornece informações técnicas necessárias para publicação no Marketplace.

Informações podem incluir:

- identificador do módulo;
- nome;
- versão;
- contratos;
- dependências;
- compatibilidade;
- recursos disponíveis;
- requisitos técnicos.

---

## Catálogo de módulos

O Marketplace utiliza essas informações para construir sua visão de catálogo.

O catálogo adiciona informações de ecossistema:

- descrição funcional;
- categoria;
- produtor;
- documentação;
- disponibilidade;
- modelo de distribuição.

---

## Publicação de módulos

O processo de publicação segue:
Module Created

    |
    v

Technical Validation

    |
    v

Marketplace Submission

    |
    v

Approval

    |
    v

Published Capability


---

## Versionamento

A Module Platform mantém o versionamento técnico dos módulos.

O Marketplace utiliza essas versões para:

- disponibilização;
- compatibilidade;
- atualização;
- histórico.

---

## Dependências

A Module Platform fornece informações sobre dependências técnicas.

O Marketplace utiliza essas informações para:

- apresentar requisitos;
- validar instalação;
- orientar consumidores.

---

## Distribuição

O Marketplace coordena a disponibilização dos módulos.

A entrega dos artefatos permanece responsabilidade das capacidades específicas de distribuição.

Integração:

- Package Distribution.

---

## Segurança

A publicação e consumo de módulos devem respeitar políticas de Security.

Security controla:

- identidade;
- permissões;
- autorização;
- acesso aos recursos.

---

## Observabilidade

A integração deve produzir informações operacionais.

Exemplos:

- módulos publicados;
- versões distribuídas;
- instalações;
- falhas;
- consumo.

Integração:

- Observability;
- Execution Log.

---

## Rastreabilidade

Eventos relevantes devem ser registrados.

Exemplos:

- módulo registrado;
- publicação criada;
- versão disponibilizada;
- instalação realizada;
- atualização executada.

Integrações:

- Execution Log;
- Execution History.

---

## Governança

A integração deve garantir:

- fonte técnica oficial;
- publicação controlada;
- compatibilidade;
- versionamento;
- histórico.

---

## Evolução futura

A integração poderá suportar:

- publicação automática;
- pipelines de entrega;
- validação automatizada;
- descoberta inteligente;
- marketplace de parceiros.

---

## Resultado esperado

A integração entre Marketplace e Module Platform estabelece uma ponte controlada entre a infraestrutura técnica de módulos e o ecossistema de distribuição da Deja Platform, permitindo evolução sustentável e governada das capacidades.