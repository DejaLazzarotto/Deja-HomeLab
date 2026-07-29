# Features

## Objetivo

Este documento apresenta as Features da Deja Indicadores.

Cada Feature representa uma funcionalidade identificável pelo usuário e pertence obrigatoriamente a um único Épico.

As Features constituem a base para a definição das Histórias de Usuário, da Arquitetura Funcional e da implementação.

---

# EP-001 — Gestão de Empresas

## FE-001 — Cadastro de Empresas

Permite cadastrar e manter empresas atendidas pela plataforma.

## FE-002 — Cadastro de Unidades Organizacionais

Permite organizar filiais, unidades e estruturas administrativas.

## FE-003 — Cadastro de Setores

Permite representar a estrutura organizacional da empresa.

## FE-004 — Cadastro de Responsáveis

Permite associar pessoas responsáveis pelos indicadores e processos.

---

# EP-002 — Gestão de Indicadores

## FE-005 — Cadastro de Indicadores

Define os indicadores monitorados pela organização.

## FE-006 — Fórmulas de Cálculo

Permite configurar a forma de cálculo dos indicadores.

## FE-007 — Definição de Metas

Permite estabelecer metas para cada indicador.

## FE-008 — Periodicidade

Define a frequência de apuração dos indicadores.

## FE-009 — Classificação de Indicadores

Organiza indicadores por categorias e níveis hierárquicos.

---

# EP-003 — Coleta de Dados

## FE-010 — Coleta Manual

Registro manual dos valores dos indicadores.

## FE-011 — Importação de Dados

Importação de dados provenientes de sistemas externos.

## FE-012 — Validação de Dados

Validação das informações antes da consolidação.

## FE-013 — Histórico de Coletas

Armazena todas as coletas realizadas.

---

# EP-004 — Diagnóstico Organizacional

## FE-014 — Análise de Desempenho

Avalia o comportamento dos indicadores.

## FE-015 — Identificação de Desvios

Detecta indicadores fora do comportamento esperado.

## FE-016 — Consolidação de Resultados

Apresenta análises consolidadas da organização.

---

# EP-005 — Planejamento

## FE-017 — Objetivos Estratégicos

Cadastro dos objetivos organizacionais.

## FE-018 — Planos de Ação

Gerenciamento dos planos associados às metas.

## FE-019 — Acompanhamento das Metas

Monitoramento da evolução dos objetivos.

---

# EP-006 — Monitoramento

## FE-020 — Painel de Acompanhamento

Visualização contínua dos indicadores.

## FE-021 — Alertas

Notificações para situações críticas.

## FE-022 — Exceções

Tratamento de indicadores fora dos limites estabelecidos.

---

# EP-007 — Dashboards

## FE-023 — Dashboards Executivos

Painéis voltados à alta gestão.

## FE-024 — Dashboards Gerenciais

Painéis destinados aos gestores.

## FE-025 — Dashboards Operacionais

Painéis para acompanhamento operacional.

## FE-026 — Widgets Analíticos

Componentes reutilizáveis para composição dos dashboards.

---

# EP-008 — Relatórios

## FE-027 — Relatórios Gerenciais

Relatórios para acompanhamento da gestão.

## FE-028 — Relatórios Executivos

Relatórios consolidados para tomada de decisão.

## FE-029 — Exportação de Dados

Exportação para formatos externos.

---

# EP-009 — Administração

## FE-030 — Usuários

Cadastro e administração de usuários.

## FE-031 — Perfis

Definição dos perfis de acesso.

## FE-032 — Permissões

Controle granular de permissões.

## FE-033 — Auditoria

Registro das operações realizadas pelos usuários.

## FE-034 — Configurações Gerais

Configurações institucionais do produto.

---

## Convenções

Cada Feature deverá manter rastreabilidade com:

```text
Capacidade
        ↓
Épico
        ↓
Feature
        ↓
História de Usuário
        ↓
Arquitetura Funcional
        ↓
Especificação Funcional
        ↓
Código
        ↓
Testes
        ↓
Documentação
```

As Features representam o planejamento funcional do produto e serão refinadas em Histórias de Usuário durante a elaboração da Arquitetura Funcional.