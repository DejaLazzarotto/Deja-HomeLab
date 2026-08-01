# 06. Ciclo de Vida das Aplicações

## Objetivo

A Workspace Applications estabelece um ciclo de vida institucional único para todas as aplicações executadas no Workspace da Deja Platform.

Esse ciclo de vida garante previsibilidade operacional, controle centralizado, rastreabilidade completa e integração consistente com as demais capacidades da plataforma.

Toda aplicação percorre estados bem definidos, administrados exclusivamente pela Workspace Applications.

---

## Princípios

O ciclo de vida é baseado nos seguintes princípios:

- gerenciamento centralizado;
- transições determinísticas;
- estados bem definidos;
- isolamento entre aplicações;
- rastreabilidade completa;
- operações auditáveis;
- recuperação segura;
- integração com observabilidade.

Nenhuma aplicação controla diretamente seu próprio ciclo de vida.

---

## Estados institucionais

Toda aplicação pode assumir os seguintes estados:

```text
Registered
      │
      ▼
Discovered
      │
      ▼
Loaded
      │
      ▼
Initialized
      │
      ▼
Active
      │
      ├───────────────┐
      ▼               │
Suspended             │
      │               │
      └──────► Active │
                      │
                      ▼
                 Stopping
                      │
                      ▼
                 Unloaded
```

Cada transição é controlada institucionalmente.

---

## Registered

A aplicação foi registrada na plataforma.

Nesse estado encontram-se disponíveis:

- identidade institucional;
- metadados;
- contratos públicos;
- informações de compatibilidade.

Ainda não existe código carregado em memória.

---

## Discovered

A aplicação foi localizada pelo mecanismo de descoberta.

Neste estágio são validados:

- disponibilidade;
- versão;
- dependências;
- compatibilidade;
- políticas de execução.

Somente aplicações válidas prosseguem.

---

## Loaded

Os artefatos necessários foram carregados.

Inclui:

- módulos;
- recursos;
- configurações;
- descritores;
- componentes necessários.

Ainda não existe execução ativa.

---

## Initialized

A aplicação executa sua inicialização institucional.

São preparados:

- contexto;
- serviços;
- integração com Workspace Runtime;
- eventos;
- recursos compartilhados.

Após sucesso, a aplicação está apta para ativação.

---

## Active

Representa a aplicação em execução.

Neste estado:

- recebe eventos;
- disponibiliza funcionalidades;
- utiliza serviços institucionais;
- participa normalmente do Workspace.

É o estado operacional principal.

---

## Suspended

A aplicação permanece carregada, porém temporariamente inativa.

Pode ocorrer por:

- economia de recursos;
- políticas administrativas;
- manutenção;
- suspensão operacional.

A retomada ocorre sem novo carregamento.

---

## Stopping

Representa o processo controlado de encerramento.

Inclui:

- encerramento ordenado;
- liberação de recursos;
- cancelamento de operações;
- persistência necessária;
- encerramento de integrações.

Nenhuma interrupção abrupta é permitida.

---

## Unloaded

Todos os recursos foram removidos.

Neste estado:

- memória liberada;
- contexto destruído;
- eventos removidos;
- integrações encerradas;
- Runtime atualizado.

A aplicação poderá ser carregada novamente quando necessário.

---

## Controle institucional

Todas as transições são administradas pela Workspace Applications.

Durante o ciclo de vida são produzidos registros para:

- auditoria;
- observabilidade;
- métricas;
- rastreabilidade;
- diagnóstico operacional.

Esse modelo garante estabilidade, previsibilidade e governança sobre todas as aplicações executadas no Workspace.