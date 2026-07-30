# 05. Componentes

## Objetivo

Esta seção descreve os componentes que compõem a arquitetura interna do Execution Engine.

O Execution Engine é responsável por transformar decisões institucionais em execuções operacionais controladas, coordenando workflows, tarefas, integrações, recursos e monitoramento.

Cada componente possui responsabilidade única, interfaces explícitas e baixo acoplamento, permitindo evolução independente da implementação.

---

# Visão Geral

A arquitetura institucional do Execution Engine é composta pelos seguintes componentes:

```text
Execution Engine
│
├── Execution Definition Registry
├── Execution Plan Builder
├── Execution Orchestrator
├── Workflow Engine
├── Execution Scheduler
├── Task Dispatcher
├── Task Executor
├── Integration Manager
├── Resource Manager
├── Execution State Manager
├── Retry Manager
├── Compensation Manager
├── Execution Monitor
├── Execution Event Bus
├── Execution Trace Builder
├── Execution Instance Builder
└── Execution Repository
```

Cada componente representa um serviço institucional da camada de execução.

---

## Execution Definition Registry

Responsável pelo gerenciamento das Execution Definitions.

Suas responsabilidades incluem:

- registrar definições;
- controlar versões;
- recuperar definições vigentes;
- disponibilizar definições ao processo de execução.

---

## Execution Plan Builder

Constrói o plano operacional da execução.

É responsável por:

- interpretar a Decision Instance;
- selecionar a Execution Definition;
- gerar o Execution Plan;
- organizar tarefas;
- estabelecer dependências.

O plano produzido é imutável durante a execução.

---

## Execution Orchestrator

Representa o núcleo do Execution Engine.

É responsável por:

- iniciar execuções;
- coordenar os componentes internos;
- controlar o fluxo operacional;
- acompanhar o progresso;
- finalizar execuções.

Nenhum outro componente controla diretamente o processo de execução.

---

## Workflow Engine

Gerencia o fluxo operacional definido pelo Execution Plan.

Entre suas responsabilidades:

- sequência de tarefas;
- paralelismo;
- sincronização;
- dependências;
- transições.

O Workflow Engine interpreta exclusivamente o plano aprovado.

---

## Execution Scheduler

Responsável pelo agendamento das tarefas.

Pode controlar:

- execução imediata;
- execução futura;
- execução recorrente;
- janelas operacionais;
- prioridades.

---

## Task Dispatcher

Seleciona quais tarefas podem iniciar.

Considera:

- dependências;
- recursos disponíveis;
- políticas;
- estado da execução.

---

## Task Executor

Executa efetivamente cada tarefa operacional.

Pode executar:

- comandos internos;
- chamadas de API;
- workflows;
- scripts;
- integrações;
- automações.

O Executor não toma decisões.

Ele apenas executa o plano aprovado.

---

## Integration Manager

Gerencia todas as integrações externas.

Pode controlar integração com:

- ERPs;
- CRMs;
- bancos de dados;
- APIs;
- mensageria;
- sistemas corporativos.

As integrações permanecem desacopladas do Workflow.

---

## Resource Manager

Controla os recursos utilizados durante a execução.

Entre eles:

- usuários;
- serviços;
- filas;
- conexões;
- arquivos;
- infraestrutura.

Permite controle de disponibilidade e utilização.

---

## Execution State Manager

Controla o estado institucional da execução.

Exemplos:

- Planned
- Waiting
- Running
- Paused
- Completed
- Cancelled
- Failed

Toda mudança de estado gera eventos.

---

## Retry Manager

Responsável pelo reprocessamento controlado.

Pode aplicar estratégias como:

- retry imediato;
- retry programado;
- retry exponencial;
- limite de tentativas.

O Retry Manager preserva a consistência da execução.

---

## Compensation Manager

Responsável pelas operações de compensação.

Quando uma execução não puder ser concluída, esse componente poderá:

- desfazer operações;
- executar compensações;
- restaurar estados anteriores;
- registrar inconsistências.

A compensação não altera a Decision Instance.

---

## Execution Monitor

Monitora continuamente o andamento das execuções.

Pode acompanhar:

- progresso;
- duração;
- gargalos;
- falhas;
- utilização de recursos;
- SLA.

---

## Execution Event Bus

Centraliza todos os eventos produzidos durante a execução.

Entre eles:

- execução iniciada;
- tarefa iniciada;
- tarefa concluída;
- mudança de estado;
- falha;
- retry;
- compensação;
- conclusão.

Todos os eventos permanecem rastreáveis.

---

## Execution Trace Builder

Constrói toda a rastreabilidade da execução.

Mantém vínculos com:

- Decision Instance;
- Execution Plan;
- tarefas;
- eventos;
- integrações;
- recursos;
- resultados.

---

## Execution Instance Builder

Responsável pela criação da Execution Instance.

Cada instância deverá conter:

- identificador único;
- Decision Instance;
- plano utilizado;
- estado;
- histórico;
- eventos;
- resultados;
- rastreabilidade;
- versão.

---

## Execution Repository

Representa a fonte oficial das execuções realizadas.

Suas responsabilidades incluem:

- persistência;
- histórico;
- auditoria;
- consultas;
- versionamento;
- recuperação.

---

## Organização arquitetural

O Execution Engine constitui a camada operacional do Núcleo de Inteligência da Deja Indicadores.

Sua arquitetura foi concebida para suportar desde execuções simples até workflows corporativos complexos, preservando os princípios de modularidade, rastreabilidade, governança e independência tecnológica.

Essa organização permite que o Execution Engine evolua futuramente para uma infraestrutura institucional de orquestração de processos reutilizável por toda a Deja Platform.