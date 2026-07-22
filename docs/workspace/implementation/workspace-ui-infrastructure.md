# Workspace UI Infrastructure

## W3.7 — Workspace UI Infrastructure

### Objetivo

A Workspace UI Infrastructure estabelece a infraestrutura institucional responsável pela organização das interações visuais do Deja Workspace.

Esta camada define contratos e registries utilizados pelos componentes da interface, mantendo total independência da lógica de negócio.

Toda interação do usuário deverá ser mediada pela arquitetura oficial do Workspace SDK.

---

# Filosofia

A interface do Workspace nunca executa lógica de negócio diretamente.

Todo elemento visual deverá produzir uma Workspace Action.

A Action poderá executar um Workspace Command.

O Command será responsável pela execução da lógica de negócio.

O fluxo oficial passa a ser:

```
User Interface
        │
        ▼
Workspace Menu
Workspace Toolbar
Context Menu
Command Palette
Widgets
Dashboards
        │
        ▼
Workspace Action
        │
        ▼
Workspace Command
        │
        ▼
Business Logic
```

---

# Workspace Menu

O Workspace Menu representa a infraestrutura responsável pela definição dos menus institucionais do Workspace.

Menus descrevem apenas:

- estrutura;
- organização;
- localização;
- ações disponíveis.

Menus não executam lógica de negócio.

Cada item referencia exclusivamente um:

```
WorkspaceActionId
```

Nunca:

```
WorkspaceCommandId
```

---

# Workspace Menu Registry

O Workspace Menu Registry constitui o repositório oficial dos menus registrados.

Responsabilidades:

- registrar menus;
- impedir identificadores duplicados;
- localizar menus;
- remover menus;
- consultar menus por localização;
- manter ordenação institucional.

A ordenação ocorre através da propriedade:

```
order
```

permitindo composição consistente da interface.

---

# Integração com Workspace Runtime

O Workspace Runtime passa a incorporar oficialmente o Workspace Menu Registry.

O Runtime disponibiliza operações para:

- registrar menus;
- registrar múltiplos menus;
- remover menus;
- consultar menus;
- consultar menus por localização.

Toda infraestrutura permanece desacoplada do framework Angular.

---

# Integração com Workspace Actions

Menus nunca executam Commands diretamente.

Cada item de menu referencia uma Workspace Action.

Fluxo oficial:

```
Workspace Menu
        │
        ▼
Workspace Action
        │
        ▼
Workspace Command
        │
        ▼
Business Logic
```

Este desacoplamento preserva:

- reutilização;
- extensibilidade;
- testabilidade;
- independência da interface.

---

# Componentes futuros

Esta infraestrutura servirá como base para:

- Workspace Toolbar
- Workspace Context Menu
- Workspace Command Palette
- Workspace Widgets
- Workspace Dashboards

Todos utilizarão exclusivamente Workspace Actions como mecanismo de interação.

---

# Arquitetura

```
Workspace Runtime
        │
        ├── Workspace Commands
        ├── Workspace Actions
        ├── Workspace Menus
        ├── Runtime Extensions
        ├── Runtime Events
        └── Runtime Hooks
```

---

# Estado da implementação

Implementado nesta fase:

- Workspace Menu API
- Workspace Menu Registry
- integração ao Workspace Runtime
- atualização da Public API

---

# Próxima etapa

W3.7.2 — Workspace Toolbar Infrastructure

Objetivos:

- Workspace Toolbar API
- Workspace Toolbar Registry
- integração ao Workspace Runtime
- integração com Workspace Actions

A Toolbar utilizará integralmente a infraestrutura estabelecida nesta fase.