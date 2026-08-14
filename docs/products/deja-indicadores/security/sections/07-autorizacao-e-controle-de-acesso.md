# 07. Autorização e Controle de Acesso

## Objetivo

Esta seção descreve a arquitetura institucional de autorização e controle de acesso do Security da Deja Platform.

A autorização é responsável por determinar quais operações uma identidade autenticada pode executar sobre determinados recursos, considerando papel, escopo, contexto e políticas institucionais.

---

# Conceito de Autorização

A autorização representa a decisão de permitir ou negar uma operação solicitada.

Enquanto a autenticação responde:

> Quem é a entidade?

A autorização responde:

> O que essa entidade pode fazer sobre este recurso e dentro de qual escopo?

---

# Modelo de Autorização

O modelo considera a relação entre:

- identidade;
- papel;
- recurso;
- ação;
- escopo;
- contexto;
- política;
- decisão.

Representação conceitual:

```text
Identity
    +
Role
    +
Resource
    +
Action
    +
Scope
    +
Context
    ↓
Policy Evaluation
    ↓
Authorization Decision
```

---

# Recursos Protegidos

O controle de acesso pode ser aplicado sobre:

- Organizações;
- Tenants;
- Ambientes;
- usuários;
- dados;
- APIs;
- serviços;
- workflows;
- execuções;
- dashboards;
- relatórios;
- módulos;
- configurações;
- modelos analíticos;
- recursos administrativos.

---

# Ações Controladas

As operações podem representar:

- listar;
- consultar;
- criar;
- alterar;
- executar;
- publicar;
- administrar;
- remover;
- compartilhar.

A lista de ações deve ser extensível conforme novos recursos sejam adicionados à plataforma.

---

# Authorization Service

## Responsabilidade

O Authorization Service centraliza a avaliação das permissões de acesso.

## Capacidades

Inclui:

- validação de papéis;
- validação de escopo institucional;
- resolução do escopo obrigatório para listagens;
- avaliação de políticas;
- controle de recursos;
- decisões de acesso;
- integração com componentes consumidores.

O serviço de autorização não deve confiar apenas em filtros fornecidos pelo cliente.

---

# Policy Based Access Control

O Security utiliza um modelo orientado a políticas.

As decisões de acesso são baseadas em regras institucionais versionadas.

Uma política pode considerar:

- identidade;
- papel;
- Organização;
- Tenant;
- Ambiente;
- recurso;
- operação;
- contexto;
- nível de risco.

---

# Controle Baseado em Papéis

Os papéis institucionais humanos são:

- `platform_admin`;
- `organization_admin`;
- `tenant_admin`;
- `manager`;
- `analyst`;
- `viewer`.

Papéis representam conjuntos de permissões reutilizáveis, mas não eliminam a necessidade de validar o escopo do recurso.

## Platform Admin

O `platform_admin` possui alcance global para operações administrativas da Deja Platform.

Esse papel:

- não pertence a Organização, Tenant ou Ambiente;
- pode executar operações estruturais entre Organizações;
- deve ser concedido somente a identidades internas;
- exige auditoria reforçada.

## Organization Admin

O `organization_admin` administra recursos autorizados da própria Organização.

Seu alcance inclui os Tenants e Ambientes pertencentes a essa Organização, sem permitir acesso a outras Organizações.

## Tenant Admin

O `tenant_admin` administra recursos autorizados do próprio Tenant.

Seu alcance não pode ser ampliado para outros Tenants, ainda que pertençam à mesma Organização.

## Manager

O `manager` possui permissões de gestão operacional dentro do próprio Ambiente.

O acesso a recursos institucionais de Organização, Tenant e Ambiente é somente de consulta quando explicitamente previsto pela política da capacidade.

## Analyst

O `analyst` possui permissões funcionais de análise dentro do próprio Ambiente.

Esse papel não recebe acesso administrativo por padrão.

## Viewer

O `viewer` possui permissões funcionais somente de consulta dentro do próprio Ambiente.

Esse papel não recebe acesso administrativo por padrão.

# Matriz de Acesso da Gestão de Empresas

A Gestão de Empresas é uma capacidade operacional protegida e vinculada obrigatoriamente a um Ambiente.

A propriedade institucional de uma empresa é resolvida pela hierarquia:

```text
Empresa
    │
    └── Ambiente
            │
            └── Tenant
                    │
                    └── Organização
```

A matriz de permissões da capacidade é:

| Papel | Listar e consultar | Criar, atualizar e excluir | Escopo obrigatório |
|---|---|---|---|
| `platform_admin` | permitido | permitido | global |
| `organization_admin` | permitido | permitido | própria Organização |
| `tenant_admin` | permitido | permitido | próprio Tenant |
| `manager` | permitido | permitido | próprio Ambiente |
| `analyst` | permitido | negado | próprio Ambiente |
| `viewer` | permitido | negado | próprio Ambiente |

As seguintes regras são obrigatórias:

- todas as rotas de empresas exigem autenticação Bearer;
- toda empresa pertence diretamente a um único Ambiente;
- Organização e Tenant são resolvidos pela hierarquia institucional do Ambiente;
- listagens aplicam automaticamente o escopo obrigatório da identidade;
- filtros incompatíveis com o escopo autenticado devem ser negados;
- recursos individuais devem ter seu escopo validado após a resolução interna;
- criações e atualizações devem validar o Ambiente informado e toda a sua hierarquia;
- nenhuma identidade limitada pode criar, consultar, atualizar ou excluir empresas fora do próprio escopo;
- `analyst` e `viewer` possuem acesso exclusivamente de leitura;
- as validações de papel e escopo devem existir tanto na entrada HTTP quanto na camada de serviço;
- consultas persistentes devem aplicar os filtros institucionais efetivos;
- a unicidade documental e as demais regras funcionais da Gestão de Empresas permanecem preservadas.

# Matriz de Acesso da Gestão de Indicadores

A Gestão de Indicadores é uma capacidade operacional protegida cujo escopo institucional é herdado obrigatoriamente da empresa vinculada.

O indicador permanece vinculado diretamente apenas por `company_id`. Organização, Tenant e Ambiente não devem ser duplicados no registro do indicador, pois são resolvidos pela hierarquia:

```text
Indicador
    │
    └── Empresa
            │
            └── Ambiente
                    │
                    └── Tenant
                            │
                            └── Organização
```

A matriz de permissões da capacidade é:

| Papel | Listar e consultar | Criar e atualizar | Excluir | Escopo obrigatório |
|---|---|---|---|---|
| `platform_admin` | permitido | permitido | permitido | global |
| `organization_admin` | permitido | permitido | permitido | própria Organização |
| `tenant_admin` | permitido | permitido | permitido | próprio Tenant |
| `manager` | permitido | permitido | permitido | próprio Ambiente |
| `analyst` | permitido | permitido | negado | próprio Ambiente |
| `viewer` | permitido | negado | negado | próprio Ambiente |

As seguintes regras são obrigatórias:

- todas as rotas de indicadores exigem autenticação Bearer;
- todo indicador pertence diretamente a uma única empresa;
- Ambiente, Tenant e Organização são resolvidos pela hierarquia institucional real da empresa;
- listagens aplicam automaticamente o escopo obrigatório da identidade;
- listagens podem ser restringidas por empresa, Organização, Tenant e Ambiente;
- filtros incompatíveis com o escopo autenticado devem ser negados;
- filtros por empresas fora do escopo autenticado devem ser negados;
- recursos individuais devem ter seu escopo validado após a resolução interna da empresa;
- criações devem validar a empresa informada e toda a sua hierarquia;
- atualizações devem validar tanto a empresa atual quanto a empresa de destino;
- nenhuma identidade limitada pode criar, consultar, atualizar, transferir ou excluir indicadores fora do próprio escopo;
- o `analyst` pode criar e atualizar indicadores dentro do próprio Ambiente, mas não pode excluí-los;
- o `viewer` possui acesso exclusivamente de leitura;
- exclusões permanecem restritas aos papéis de gestão;
- as validações de papel e escopo devem existir tanto na entrada HTTP quanto na camada de serviço;
- consultas persistentes devem aplicar os filtros institucionais efetivos;
- a existência da empresa, a unicidade do nome por empresa e as demais regras funcionais da Gestão de Indicadores permanecem preservadas;
- a exclusão de indicadores com medições cadastradas permanece bloqueada.

# Matriz de Acesso da Gestão de Medições

A Gestão de Medições é uma capacidade operacional protegida cujo escopo institucional é herdado obrigatoriamente do indicador e da empresa vinculados.

A medição permanece vinculada diretamente apenas por `indicator_id`. Empresa, Organização, Tenant e Ambiente não devem ser duplicados no registro da medição, pois são resolvidos pela hierarquia:

```text
Medição
    │
    └── Indicador
            │
            └── Empresa
                    │
                    └── Ambiente
                            │
                            └── Tenant
                                    │
                                    └── Organização
```

A matriz de permissões da capacidade é:

| Papel | Listar e consultar | Criar, atualizar e excluir | Escopo obrigatório |
|---|---|---|---|
| `platform_admin` | permitido | permitido | global |
| `organization_admin` | permitido | permitido | própria Organização |
| `tenant_admin` | permitido | permitido | próprio Tenant |
| `manager` | permitido | permitido | próprio Ambiente |
| `analyst` | permitido | permitido | próprio Ambiente |
| `viewer` | permitido | negado | próprio Ambiente |

As seguintes regras são obrigatórias:

- todas as rotas de medições exigem autenticação Bearer;
- toda medição pertence diretamente a um único indicador;
- empresa, Ambiente, Tenant e Organização são resolvidos pela hierarquia institucional real do indicador;
- listagens aplicam automaticamente o escopo obrigatório da identidade;
- listagens podem ser restringidas por empresa, indicador, Organização, Tenant, Ambiente e período de referência;
- filtros incompatíveis com o escopo autenticado devem ser negados;
- filtros por empresas ou indicadores fora do escopo autenticado devem ser negados;
- recursos individuais devem ter seu escopo validado após a resolução interna do indicador e da empresa;
- criações devem validar o indicador informado e toda a sua hierarquia institucional;
- atualizações devem validar tanto o indicador atual quanto o indicador de destino;
- nenhuma identidade limitada pode criar, consultar, atualizar, transferir ou excluir medições fora do próprio escopo;
- o `analyst` pode criar, consultar, atualizar e excluir medições dentro do próprio Ambiente;
- o `viewer` possui acesso exclusivamente de leitura;
- o usuário autenticado responsável pela criação deve ser registrado em `created_by`;
- a identidade criadora deve ser preservada durante atualizações;
- auditoria ampliada e registro de `updated_by` poderão ser incorporados em evolução posterior;
- exclusão lógica poderá ser avaliada em evolução posterior sem alterar a política atual;
- as validações de papel e escopo devem existir tanto na entrada HTTP quanto na camada de serviço;
- consultas persistentes devem aplicar os filtros institucionais efetivos;
- a existência do indicador, a unicidade por indicador e data de referência e as demais regras funcionais da Gestão de Medições permanecem preservadas.

---

# Matriz de Acesso dos Dashboards

Os Dashboards constituem uma capacidade gerencial exclusivamente de consulta. Seu escopo institucional é herdado das empresas, dos indicadores e das medições utilizados nas agregações.

Os dados consolidados são resolvidos pela hierarquia:

```text
Dashboard
    │
    ├── Empresa
    │       │
    │       └── Ambiente
    │               │
    │               └── Tenant
    │                       │
    │                       └── Organização
    │
    └── Indicador
            │
            └── Medição
```

A matriz de permissões da capacidade é:

| Papel | Consultar visão gerencial | Escopo obrigatório |
|---|---|---|
| `platform_admin` | permitido | global |
| `organization_admin` | permitido | própria Organização |
| `tenant_admin` | permitido | próprio Tenant |
| `manager` | permitido | próprio Ambiente |
| `analyst` | permitido | próprio Ambiente |
| `viewer` | permitido | próprio Ambiente |

As seguintes regras são obrigatórias:

- todas as rotas de dashboards exigem autenticação Bearer;
- dashboards são exclusivamente de leitura e não expõem operações de criação, atualização ou exclusão;
- empresas, indicadores e medições somente podem participar de agregações quando pertencem ao escopo efetivo da identidade;
- listagens, contagens, agrupamentos por status, históricos e KPIs devem aplicar o mesmo escopo institucional;
- o escopo é resolvido pela relação entre empresa, Ambiente, Tenant e Organização;
- medições herdam o escopo do indicador e da empresa vinculados;
- consultas podem ser restringidas por Organização, Tenant, Ambiente, empresa, indicador e período de referência;
- filtros institucionais compatíveis podem restringir adicionalmente o resultado;
- filtros que tentem ampliar o escopo autenticado devem ser negados;
- filtros por empresas ou indicadores existentes fora do escopo autenticado devem ser negados;
- empresas ou indicadores inexistentes preservam a semântica funcional de recurso não encontrado;
- filtros simultâneos de empresa e indicador autorizados, mas sem relação entre si, devem produzir um dashboard vazio;
- a ausência de dados no escopo autorizado deve produzir totais zerados e coleções vazias;
- identidades limitadas não podem incorporar dados de outras Organizações, Tenants ou Ambientes em totais, status, KPIs ou históricos;
- as validações de papel e escopo devem existir tanto na entrada HTTP quanto na camada de serviço;
- o escopo institucional deve ser aplicado diretamente nas consultas persistentes;
- dados globais não devem ser carregados para posterior filtragem apenas em memória;
- consumidores internos do dashboard, incluindo relatórios, devem propagar a identidade autenticada e não podem contornar a autorização;
- o cálculo de atingimento, a situação perante a meta, os filtros inclusivos de período e as demais regras funcionais permanecem preservados.

---

# Matriz de Acesso dos Relatórios

Os Relatórios constituem uma capacidade gerencial exclusivamente de consulta. Seu escopo institucional é herdado integralmente do Dashboard utilizado para consolidar empresas, indicadores e medições.

A matriz de permissões da capacidade é:

| Papel | Consultar relatório gerencial | Escopo obrigatório |
|---|---|---|
| `platform_admin` | permitido | global |
| `organization_admin` | permitido | própria Organização |
| `tenant_admin` | permitido | próprio Tenant |
| `manager` | permitido | próprio Ambiente |
| `analyst` | permitido | próprio Ambiente |
| `viewer` | permitido | próprio Ambiente |

As seguintes regras são obrigatórias:

- todas as rotas de relatórios exigem autenticação Bearer;
- relatórios são exclusivamente de leitura e não expõem operações de criação, atualização ou exclusão;
- a identidade autenticada deve ser propagada da entrada HTTP para o serviço de relatórios e deste para o serviço de dashboard;
- a validação dos papéis leitores deve ocorrer na entrada HTTP e novamente na camada de serviço de relatórios;
- o serviço de dashboard deve repetir suas próprias validações de papel, recursos e escopo;
- relatórios podem ser restringidos por Organização, Tenant, Ambiente, empresa, indicador e período de referência;
- filtros institucionais compatíveis podem restringir adicionalmente o resultado;
- filtros que tentem ampliar o escopo autenticado devem ser negados;
- filtros por empresas ou indicadores existentes fora do escopo autenticado devem ser negados;
- empresas ou indicadores inexistentes preservam a semântica funcional de recurso não encontrado;
- filtros simultâneos de empresa e indicador autorizados, mas sem relação entre si, devem produzir um relatório vazio;
- a ausência de dados no escopo autorizado deve produzir totais zerados e coleções vazias;
- os metadados do relatório devem refletir exatamente os filtros solicitados pelo consumidor;
- filtros institucionais aplicados implicitamente pela autorização não devem ser apresentados como se tivessem sido solicitados pelo consumidor;
- identidades limitadas não podem incorporar dados de outras Organizações, Tenants ou Ambientes em totais, agrupamentos, KPIs ou históricos;
- o escopo institucional deve ser aplicado diretamente nas consultas persistentes reutilizadas pelo dashboard;
- dados globais não devem ser carregados para posterior filtragem apenas em memória;
- chamadas internas não podem utilizar o relatório ou o dashboard sem propagar uma identidade autenticada;
- títulos, data de geração, cálculos gerenciais, filtros inclusivos de período e contratos funcionais permanecem preservados.

---

# Controle Baseado em Escopo

As decisões de autorização devem considerar os seguintes níveis:

```text
Plataforma
    │
    └── Organização
            │
            └── Tenant
                    │
                    └── Ambiente
```

Uma identidade não pode ampliar o próprio escopo por meio de:

- parâmetros de rota;
- filtros de consulta;
- dados do corpo da requisição;
- cabeçalhos controlados pelo cliente;
- referências indiretas a outros recursos.

O escopo efetivo é formado pelos vínculos da identidade autenticada e pelos filtros solicitados, sempre adotando o limite mais restritivo.

---

# Controle Baseado em Atributos

Além de papéis e escopo, decisões podem considerar atributos.

Exemplos:

- tipo de usuário;
- estado da identidade;
- estado do recurso;
- classificação do recurso;
- contexto operacional;
- origem da solicitação;
- nível de risco.

---

# Princípio do Menor Privilégio

O controle de acesso segue o princípio de menor privilégio.

Cada identidade deve possuir somente as permissões necessárias para executar suas responsabilidades.

Permissões globais não devem ser concedidas a administradores de clientes.

Operações estruturais de alto impacto devem permanecer restritas ao menor conjunto possível de identidades.

---

# Defesa em Profundidade

A autorização deve ser aplicada em mais de uma camada.

A camada de entrada deve:

- exigir autenticação;
- validar os papéis permitidos;
- rejeitar operações sem permissão.

A camada de serviço deve:

- repetir a validação dos papéis;
- validar o escopo do recurso consultado;
- validar o escopo dos dados recebidos;
- aplicar escopo obrigatório às listagens;
- impedir chamadas internas que contornem a proteção HTTP.

A persistência deve fornecer consultas capazes de filtrar os recursos pelo escopo institucional efetivo.

---

# Listagens Protegidas

Toda listagem protegida deve aplicar automaticamente o escopo da identidade.

As seguintes regras são obrigatórias:

- `platform_admin` pode realizar listagens globais quando a política permitir;
- identidades institucionais devem receber escopo obrigatório de Organização;
- identidades de Tenant devem receber escopo obrigatório de Tenant;
- identidades de Ambiente devem receber escopo obrigatório de Ambiente;
- filtros compatíveis podem restringir ainda mais o resultado;
- filtros incompatíveis devem produzir negação de acesso;
- a ausência de filtro não pode resultar em listagem global para uma identidade limitada.

---

# Recursos Individuais

A autorização de um recurso individual deve ocorrer após sua resolução interna e antes de sua exposição ou alteração.

A política deve comparar o escopo do recurso com o escopo da identidade autenticada.

Tentativas de acesso cruzado devem ser negadas sem retornar os dados protegidos.

---

# Criações e Atualizações

Dados recebidos em operações de criação ou atualização não são considerados confiáveis para fins de autorização.

Antes da persistência, a aplicação deve:

1. validar o papel da identidade;
2. resolver os recursos institucionais referenciados;
3. validar a consistência entre Organização, Tenant e Ambiente;
4. comparar o escopo resolvido com a identidade autenticada;
5. executar as regras funcionais da capacidade;
6. persistir somente após todas as validações.

---

# Decisão de Autorização

Toda decisão deve possuir:

- identidade avaliada;
- papel avaliado;
- recurso solicitado;
- ação solicitada;
- escopo solicitado;
- política aplicada;
- resultado;
- justificativa.

Resultados possíveis:

- permitido;
- negado;
- condicionado.

---

# Semântica HTTP

As APIs protegidas devem distinguir autenticação de autorização.

## Falha de Autenticação

Quando a identidade não puder ser autenticada:

- responder com HTTP `401`;
- utilizar erro institucional de autenticação;
- enviar `WWW-Authenticate: Bearer` quando aplicável.

## Falha de Autorização

Quando a identidade estiver autenticada, mas não possuir papel ou escopo suficiente:

- responder com HTTP `403`;
- utilizar erro institucional de acesso negado;
- não enviar `WWW-Authenticate`.

---

# Integração com Execução

Antes de executar uma operação protegida:

1. a identidade é autenticada;
2. o papel é validado;
3. o recurso e seu escopo são identificados;
4. a política aplicável é localizada;
5. a autorização é avaliada;
6. a execução é liberada ou bloqueada.

Fluxo:

```text
Request
   ↓
Authentication
   ↓
Role Validation
   ↓
Scope Validation
   ↓
Policy Evaluation
   ↓
Execution
   ↓
Audit
```

---

# Auditoria

Todas as decisões relevantes de autorização devem ser registradas.

Exemplos:

- acesso concedido;
- acesso negado;
- tentativa de acesso cruzado;
- utilização de alcance global;
- alteração de permissões;
- alteração de políticas.

Operações executadas por `platform_admin` devem ser claramente identificáveis.

---

# Integração Institucional

O controle de acesso é utilizado por:

- Tenant Management;
- Administration Platform;
- User Management;
- Execution Engine;
- Workflow Engine;
- Intelligence Core;
- Data Pipeline;
- Workspace;
- APIs;
- serviços internos;
- integrações externas.

Cada capacidade deve definir sua própria matriz de permissões, mantendo os papéis, escopos e princípios estabelecidos pelo Security.

---

# Benefícios Arquiteturais

A arquitetura proporciona:

- controle centralizado;
- políticas consistentes;
- separação entre administração global e administração de clientes;
- isolamento entre Organizações, Tenants e Ambientes;
- segurança escalável;
- rastreabilidade;
- suporte a ambientes corporativos complexos.