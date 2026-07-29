# Modelo de Capacidades da Deja Indicadores

## Objetivo

Este documento apresenta a decomposição institucional das capacidades da Deja Indicadores.

O modelo estabelece uma visão hierárquica do conhecimento do produto, organizando suas responsabilidades de negócio de forma independente da implementação, da interface do usuário e da tecnologia utilizada.

Cada capacidade representa uma competência permanente do produto e constitui a origem para a construção do Backlog de Valor e das futuras Arquiteturas Funcionais.

---

# Modelo Hierárquico

A Deja Indicadores é organizada segundo a seguinte estrutura institucional.

```text
Produto
    ↓
Capacidade
    ↓
Subcapacidade
    ↓
Serviço de Negócio
```

Essa decomposição garante que todas as funcionalidades do produto possam ser rastreadas até uma capacidade claramente definida.

---

# Árvore Institucional

```text
Deja Indicadores
│
├── Gestão de Empresas
│   │
│   ├── Cadastro de Empresas
│   ├── Gestão de Filiais
│   ├── Usuários
│   ├── Perfis de Acesso
│   └── Configurações Organizacionais
│
├── Gestão de Indicadores
│   │
│   ├── Cadastro de Indicadores
│   ├── Categorias
│   ├── Fórmulas
│   ├── Metas
│   ├── Unidades de Medida
│   └── Histórico
│
├── Coleta de Dados
│   │
│   ├── Coleta Manual
│   ├── Importação
│   ├── Integrações
│   ├── Validação
│   └── Consolidação
│
├── Diagnóstico Organizacional
│   │
│   ├── Maturidade
│   ├── Avaliações
│   ├── Questionários
│   ├── Pontuação
│   └── Recomendações
│
├── Planejamento
│   │
│   ├── Objetivos Estratégicos
│   ├── Planos de Ação
│   ├── Metas
│   ├── Responsáveis
│   └── Prioridades
│
├── Monitoramento
│   │
│   ├── Acompanhamento
│   ├── Alertas
│   ├── Tendências
│   ├── Desvios
│   └── Histórico
│
├── Dashboards
│   │
│   ├── Dashboards Executivos
│   ├── Dashboards Operacionais
│   ├── Widgets
│   ├── Filtros
│   └── Compartilhamento
│
├── Relatórios
│   │
│   ├── Relatórios Gerenciais
│   ├── Exportação
│   ├── Impressão
│   ├── Agendamento
│   └── Distribuição
│
└── Administração
    │
    ├── Configurações
    ├── Auditoria
    ├── Permissões
    ├── Logs
    └── Parametrizações
```

---

# Critérios de Organização

A decomposição das capacidades segue os seguintes princípios:

- cada capacidade possui uma responsabilidade de negócio claramente definida;
- capacidades podem ser decompostas em subcapacidades;
- subcapacidades originam serviços de negócio;
- serviços de negócio originam o Backlog de Valor;
- a implementação deverá preservar essa estrutura hierárquica.

---

# Rastreabilidade

Toda entrega do produto deverá seguir o fluxo institucional abaixo.

```text
Capacidade
        ↓
Subcapacidade
        ↓
Serviço de Negócio
        ↓
Backlog de Valor
        ↓
Arquitetura Funcional
        ↓
Especificação Funcional
        ↓
Implementação
        ↓
Testes
        ↓
Documentação
```

Esse modelo constitui a referência institucional para toda a evolução da Deja Indicadores.