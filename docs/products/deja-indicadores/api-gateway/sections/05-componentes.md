# 05. Componentes

## Objetivo

Esta seção descreve os componentes arquiteturais que compõem o API Gateway da Deja Platform.

Os componentes representam as responsabilidades técnicas necessárias para exposição, controle, processamento e governança das APIs.

---

# Visão geral dos componentes

O API Gateway é composto por componentes especializados, cada um responsável por uma etapa específica do ciclo de vida de uma chamada.

Principais componentes:

- API Registry;
- API Exposure Manager;
- Request Gateway;
- Authentication Adapter;
- Authorization Manager;
- Policy Engine;
- Request Context Manager;
- Router;
- Service Resolver;
- Execution Dispatcher;
- Response Manager;
- API Lifecycle Manager;
- Audit Integration;
- Observability Integration.

---

# API Registry

## Responsabilidade

O API Registry é o catálogo institucional das APIs disponibilizadas pela plataforma.

Ele mantém informações sobre:

- APIs existentes;
- versões;
- contratos;
- estados;
- permissões;
- metadados.

---

## Funções principais

Responsável por:

- registrar APIs;
- consultar definições;
- controlar versões;
- disponibilizar informações para resolução.

---

# API Exposure Manager

## Responsabilidade

Controla a publicação das APIs.

Responsável por:

- disponibilizar endpoints;
- administrar exposição;
- controlar disponibilidade;
- gerenciar contratos publicados.

---

# Request Gateway

## Responsabilidade

Representa o ponto inicial de entrada das chamadas.

Responsável por:

- receber requisições;
- validar estrutura inicial;
- criar contexto;
- encaminhar processamento.

---

# Authentication Adapter

## Responsabilidade

Realiza integração com o Security para autenticação.

Responsável por:

- validar identidade;
- interpretar credenciais;
- estabelecer contexto de segurança.

---

# Authorization Manager

## Responsabilidade

Controla se o consumidor possui permissão para executar determinada operação.

Responsável por:

- verificar permissões;
- aplicar regras de acesso;
- validar escopo.

---

# Policy Engine

## Responsabilidade

Executa políticas institucionais aplicáveis às chamadas.

Pode controlar:

- limites;
- restrições;
- regras operacionais;
- comportamentos configuráveis.

Integra-se com Configuration.

---

# Request Context Manager

## Responsabilidade

Mantém o contexto associado a cada requisição.

O contexto pode conter:

- identidade;
- rastreamento;
- segurança;
- configuração;
- informações operacionais.

---

# Router

## Responsabilidade

Determina o destino correto da chamada.

Responsável por:

- interpretar operação;
- localizar capacidade;
- encaminhar execução.

---

# Service Resolver

## Responsabilidade

Realiza a resolução dos destinos internos.

Integra-se com:

- Service Registry;
- Runtime;
- Module System.

---

# Execution Dispatcher

## Responsabilidade

Encaminha a operação para o componente responsável.

Pode integrar-se com:

- serviços;
- módulos;
- engines;
- capacidades especializadas.

---

# Response Manager

## Responsabilidade

Padroniza respostas geradas pela plataforma.

Responsável por:

- formatos de retorno;
- tratamento de erros;
- metadados;
- rastreabilidade.

---

# API Lifecycle Manager

## Responsabilidade

Controla o ciclo de vida das APIs.

Inclui:

- criação;
- publicação;
- atualização;
- descontinuação;
- versionamento.

---

# Audit Integration

## Responsabilidade

Integra o API Gateway aos mecanismos institucionais de auditoria.

Registra:

- chamadas;
- alterações;
- eventos administrativos.

---

# Observability Integration

## Responsabilidade

Integra o Gateway ao sistema de observabilidade.

Produz:

- métricas;
- logs;
- traces;
- indicadores operacionais.

---

# Relacionamento entre componentes

Fluxo conceitual:
