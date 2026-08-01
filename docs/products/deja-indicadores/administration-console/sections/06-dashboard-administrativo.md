# 06. Dashboard Administrativo

## Objetivo

Definir a arquitetura do Dashboard Administrativo como a visão operacional principal da Administration Console, consolidando informações estratégicas, métricas institucionais e indicadores relevantes para a administração da Deja Platform.

---

## Papel do Dashboard

O Dashboard Administrativo representa a página inicial da Administration Console.

Seu objetivo é fornecer uma visão consolidada do estado operacional da plataforma, permitindo que administradores identifiquem rapidamente eventos relevantes, indicadores críticos e ações prioritárias.

O Dashboard não executa operações administrativas; ele apresenta informações provenientes das capacidades institucionais por meio de contratos públicos.

---

## Estrutura Geral

O Dashboard é organizado em áreas independentes compostas por widgets reutilizáveis.

Exemplo de organização:

- visão geral da plataforma;
- saúde dos serviços;
- organizações;
- tenants;
- usuários;
- licenças;
- marketplace;
- APIs;
- observabilidade;
- segurança;
- notificações;
- tarefas administrativas.

Cada área pode ser habilitada, reorganizada ou expandida conforme a evolução da plataforma.

---

## Widgets Administrativos

Os widgets representam a menor unidade funcional do Dashboard.

Exemplos:

- KPIs;
- gráficos;
- indicadores;
- listas resumidas;
- alertas;
- eventos recentes;
- status operacional;
- ações rápidas;
- cartões informativos.

Cada widget possui ciclo de vida independente e consome apenas APIs institucionais.

---

## Atualização das Informações

As informações exibidas podem ser atualizadas por diferentes estratégias, conforme a natureza dos dados:

- atualização sob demanda;
- atualização periódica;
- eventos em tempo real;
- notificações institucionais.

A estratégia é definida pela capacidade fornecedora das informações.

---

## Personalização

A arquitetura permite personalização controlada do Dashboard, incluindo:

- organização dos widgets;
- seleção de painéis;
- preferências visuais;
- filtros persistentes;
- atalhos administrativos.

As personalizações nunca alteram a lógica operacional da plataforma.

---

## Integração Institucional

O Dashboard integra informações provenientes de capacidades como:

- Administration Platform;
- Tenant Management;
- Security;
- Observability;
- Billing & Licensing;
- Marketplace;
- API Management;
- Configuration;
- Developer Portal.

Toda integração ocorre exclusivamente por contratos públicos.

---

## Benefícios Arquiteturais

A arquitetura do Dashboard proporciona:

- visão operacional centralizada;
- experiência consistente;
- modularidade;
- reutilização de widgets;
- baixo acoplamento;
- escalabilidade;
- facilidade de evolução;
- rastreabilidade das informações apresentadas.