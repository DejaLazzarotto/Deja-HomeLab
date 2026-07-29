# Arquitetura em Camadas

## Objetivo

Este documento define a organização arquitetural da Deja Indicadores em camadas institucionais.

A divisão em camadas estabelece responsabilidades claras, reduz o acoplamento entre componentes e favorece a evolução incremental da solução.

Cada camada possui um papel específico e comunica-se com as demais exclusivamente por contratos institucionais.

---

# Visão Geral

A arquitetura da Deja Indicadores é organizada em seis camadas principais.

```text
┌─────────────────────────────────────────────┐
│                 Cliente                     │
└─────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────┐
│            Deja Indicadores                 │
│      (Metodologia e Regras de Negócio)      │
└─────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────┐
│             Deja Platform                   │
│     (Capacidades Institucionais)            │
└─────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────┐
│              Workspace SDK                  │
│     (Experiência e Componentes)             │
└─────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────┐
│             Platform Kernel                 │
│   (Infraestrutura, Runtime e Serviços)      │
└─────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────┐
│        Infraestrutura Tecnológica           │
│ Banco de Dados • APIs • Cloud • Rede        │
└─────────────────────────────────────────────┘
```

Cada camada possui responsabilidades próprias e não deve assumir funções pertencentes às demais.

---

# Camada 1 — Cliente

Representa os usuários da solução.

Exemplos:

- empresários;
- gestores;
- consultores;
- analistas;
- administradores.

Essa camada interage exclusivamente com a interface disponibilizada pela Deja Indicadores.

Não possui conhecimento sobre a arquitetura interna da plataforma.

---

# Camada 2 — Deja Indicadores

Representa o produto comercial.

É responsável pela implementação da metodologia de gestão.

Entre suas responsabilidades estão:

- regras de negócio;
- indicadores;
- diagnósticos;
- planos de ação;
- jornadas do cliente;
- relatórios especializados;
- experiência do usuário;
- processos da metodologia.

Esta camada não implementa infraestrutura reutilizável.

Seu foco é entregar valor ao cliente.

---

# Camada 3 — Deja Platform

Representa as capacidades institucionais reutilizáveis.

Exemplos:

- autenticação;
- autorização;
- gerenciamento de usuários;
- gerenciamento de módulos;
- APIs compartilhadas;
- eventos;
- observabilidade;
- extensibilidade;
- persistência;
- serviços institucionais.

Essas capacidades podem ser utilizadas por qualquer produto construído sobre a plataforma.

A plataforma não conhece regras específicas da Deja Indicadores.

---

# Camada 4 — Workspace SDK

O Workspace SDK fornece a infraestrutura responsável pela experiência de uso da plataforma.

Entre suas responsabilidades encontram-se:

- composição de dashboards;
- gerenciamento de widgets;
- renderização;
- layout;
- comandos;
- eventos;
- ações;
- extensões;
- integração entre módulos.

O Workspace SDK atua como uma camada especializada da Deja Platform voltada à construção de aplicações modulares.

---

# Camada 5 — Platform Kernel

Representa o núcleo técnico da plataforma.

É responsável por:

- ciclo de vida dos módulos;
- runtime;
- discovery;
- dependency resolver;
- manifestos;
- bootstrap;
- configuração;
- serviços internos;
- gerenciamento de recursos;
- infraestrutura de execução.

Nenhuma regra de negócio deverá ser implementada nesta camada.

---

# Camada 6 — Infraestrutura Tecnológica

Corresponde ao ambiente onde a solução é executada.

Inclui:

- banco de dados;
- armazenamento;
- servidores;
- cloud;
- containers;
- rede;
- sistemas operacionais;
- provedores externos.

Essa camada fornece suporte operacional para toda a arquitetura.

---

# Regras de Dependência

A arquitetura segue o princípio de dependências direcionadas.

Cada camada depende apenas da camada imediatamente inferior.

Consequentemente:

- a Deja Indicadores pode utilizar capacidades da Deja Platform;
- a Deja Platform pode utilizar o Workspace SDK;
- o Workspace SDK pode utilizar o Platform Kernel;
- o Platform Kernel pode utilizar a infraestrutura tecnológica.

O fluxo inverso não é permitido.

Essa regra evita acoplamento inadequado entre camadas.

---

# Comunicação entre Camadas

Toda comunicação deverá ocorrer por contratos institucionais.

São exemplos:

- APIs;
- interfaces;
- eventos;
- comandos;
- serviços publicados;
- pontos de extensão.

O acesso direto às implementações internas de outra camada não é permitido.

---

# Benefícios da Arquitetura

A organização em camadas proporciona:

- responsabilidades claramente definidas;
- maior reutilização de capacidades;
- facilidade de manutenção;
- baixo acoplamento;
- alta coesão;
- evolução incremental;
- substituição controlada de componentes;
- maior previsibilidade arquitetural.

---

# Considerações Finais

A arquitetura em camadas constitui a estrutura organizacional da Deja Indicadores.

Ela estabelece como responsabilidades, capacidades e componentes são distribuídos ao longo da solução, preservando a independência entre infraestrutura, plataforma e produto.

Todos os documentos arquiteturais posteriores deverão respeitar a organização definida nesta especificação.