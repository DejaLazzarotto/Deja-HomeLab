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