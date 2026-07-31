# 5. Componentes

## Objetivo

Esta seção apresenta os componentes institucionais que compõem a arquitetura do Observability.

Cada componente possui responsabilidades bem definidas dentro do ciclo de vida das informações observáveis, permitindo uma arquitetura modular, escalável e de baixo acoplamento.

---

## Visão geral

O Observability é composto pelos seguintes componentes:

- Observation Collector;
- Metrics Manager;
- Log Manager;
- Trace Manager;
- Event Manager;
- Telemetry Manager;
- Correlation Engine;
- Monitoring Engine;
- Alert Manager;
- Diagnostic Engine Adapter;
- Query Service;
- Observability Repository;
- Retention Manager.

Cada componente atua sobre uma etapa específica da observabilidade institucional.

---

## Observation Collector

O Observation Collector constitui o ponto oficial de entrada das informações observáveis.

Suas responsabilidades incluem:

- receber dados produzidos pelos componentes;
- validar o formato das mensagens;
- aplicar políticas iniciais de aceitação;
- encaminhar os registros para processamento.

---

## Metrics Manager

O Metrics Manager é responsável pelo gerenciamento das métricas operacionais.

Entre suas funções encontram-se:

- consolidação de métricas;
- agregações estatísticas;
- cálculo de indicadores operacionais;
- disponibilização para monitoramento.

---

## Log Manager

O Log Manager integra-se ao Execution Log para consolidar os registros técnicos produzidos pela plataforma.

Sua responsabilidade é organizar e disponibilizar essas informações para consultas, correlação e monitoramento.

---

## Trace Manager

O Trace Manager administra os rastreamentos distribuídos das operações.

Seu objetivo é reconstruir o fluxo completo das execuções entre serviços, módulos e componentes institucionais.

---

## Event Manager

O Event Manager recebe e organiza os eventos operacionais produzidos pelos diversos componentes da plataforma.

Esses eventos representam mudanças de estado, ocorrências relevantes e notificações técnicas utilizadas pela infraestrutura de observabilidade.

---

## Telemetry Manager

O Telemetry Manager consolida informações contínuas sobre o comportamento da plataforma.

Esses dados incluem indicadores de utilização, desempenho, capacidade e funcionamento dos serviços institucionais.

---

## Correlation Engine

O Correlation Engine estabelece relacionamentos entre métricas, logs, traces, eventos e demais registros observáveis.

Sua principal responsabilidade é produzir uma visão integrada das operações executadas pela plataforma.

---

## Monitoring Engine

O Monitoring Engine acompanha continuamente o estado operacional da plataforma.

Ele utiliza as informações consolidadas para identificar comportamentos esperados, tendências e possíveis anomalias.

---

## Alert Manager

O Alert Manager avalia regras institucionais para geração automática de alertas.

Os alertas podem ser produzidos em função de:

- limites operacionais;
- degradação de desempenho;
- indisponibilidade;
- falhas recorrentes;
- eventos críticos.

---

## Diagnostic Engine Adapter

O Diagnostic Engine Adapter integra o Observability ao Diagnostic Engine.

Essa integração permite utilizar as informações observáveis como base para diagnósticos automáticos e análises inteligentes.

---

## Query Service

O Query Service disponibiliza mecanismos padronizados para consulta das informações observáveis.

Ele atende dashboards, APIs institucionais, auditorias, investigações operacionais e demais consumidores autorizados.

---

## Observability Repository

O Observability Repository representa a infraestrutura institucional responsável pelo armazenamento das informações observáveis.

A arquitetura permanece independente da tecnologia utilizada para persistência dos dados.

---

## Retention Manager

O Retention Manager administra o ciclo de vida das informações observáveis.

Entre suas responsabilidades estão:

- aplicação das políticas de retenção;
- arquivamento;
- expurgo controlado;
- conformidade com as políticas institucionais de governança.

---

## Organização arquitetural

A atuação coordenada desses componentes estabelece uma infraestrutura completa de observabilidade para a Deja Platform.

A separação explícita das responsabilidades favorece reutilização, escalabilidade, manutenção simplificada e evolução contínua da arquitetura.