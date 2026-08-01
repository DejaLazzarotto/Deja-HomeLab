# 5. Componentes

## Objetivo

Esta seção define os componentes internos que compõem o Tenant Management da Deja Platform.

Cada componente possui responsabilidades bem delimitadas e coopera para fornecer os serviços institucionais de gestão organizacional, resolução de contexto, isolamento e administração do ciclo de vida dos Tenants.

---

# Visão Geral

O Tenant Management é composto pelos seguintes componentes:

```text
Tenant Management
│
├── Organization Manager
├── Tenant Manager
├── Environment Manager
├── Tenant Context Resolver
├── Tenant Context Provider
├── Tenant Registry
├── Tenant Provisioning Manager
├── Tenant Lifecycle Manager
├── Tenant Validation Service
├── Tenant Query Service
└── Tenant Administration Service
```

Cada componente possui responsabilidade única e baixo acoplamento.

---

# Organization Manager

Responsável pela administração institucional das Organizações.

Principais responsabilidades:

- criar organizações;
- atualizar organizações;
- ativar organizações;
- suspender organizações;
- desativar organizações;
- consultar organizações;
- manter metadados institucionais.

---

# Tenant Manager

Responsável pela administração dos Tenants.

Principais responsabilidades:

- criar tenants;
- atualizar tenants;
- ativar tenants;
- suspender tenants;
- remover tenants;
- consultar tenants;
- manter informações institucionais.

O Tenant Manager representa o principal componente de gestão do modelo multi-tenant.

---

# Environment Manager

Responsável pelos Ambientes pertencentes aos Tenants.

Exemplos:

- Development;
- Homologation;
- Production;
- Sandbox.

Responsabilidades:

- criação;
- atualização;
- ativação;
- desativação;
- consulta;
- gerenciamento do ciclo de vida.

---

# Tenant Context Resolver

Responsável por determinar qual Tenant Context deverá ser utilizado durante uma execução.

Pode utilizar informações provenientes de:

- autenticação;
- API Gateway;
- eventos;
- comandos;
- mensagens;
- workflows;
- integrações.

Sua responsabilidade é produzir um Tenant Context válido antes do processamento da operação.

---

# Tenant Context Provider

Responsável por disponibilizar o Tenant Context resolvido para os demais componentes da plataforma.

Esse componente garante consistência durante toda a execução.

---

# Tenant Registry

Responsável pelo catálogo institucional de:

- organizações;
- tenants;
- ambientes.

Fornece consultas institucionais para toda a plataforma.

Não substitui o Module Registry.

---

# Tenant Provisioning Manager

Responsável pelo provisionamento das estruturas organizacionais.

Inclui:

- criação inicial;
- configuração estrutural;
- preparação dos ambientes;
- inicialização institucional;
- integração com componentes dependentes.

---

# Tenant Lifecycle Manager

Responsável pelo ciclo de vida institucional.

Estados típicos:

- Provisioning
- Active
- Suspended
- Maintenance
- Archived
- Removed

Todas as mudanças de estado são registradas institucionalmente.

---

# Tenant Validation Service

Responsável por validar:

- consistência organizacional;
- relacionamentos;
- integridade estrutural;
- existência dos recursos;
- compatibilidade das operações.

Nenhuma operação crítica deverá prosseguir sem validação.

---

# Tenant Query Service

Disponibiliza consultas institucionais para consumidores autorizados.

Exemplos:

- localizar tenant;
- localizar ambiente;
- localizar organização;
- consultar estados;
- consultar contexto.

O serviço possui natureza exclusivamente consultiva.

---

# Tenant Administration Service

Fornece operações administrativas utilizadas por ferramentas institucionais.

Entre elas:

- administração operacional;
- gerenciamento organizacional;
- manutenção estrutural;
- auditorias;
- consultas administrativas.

Não executa autenticação nem autorização.

---

# Relacionamento entre Componentes

```text
Organization Manager
            │
            ▼
Tenant Manager
            │
            ▼
Environment Manager
            │
            ▼
Tenant Context Resolver
            │
            ▼
Tenant Context Provider
            │
            ▼
Demais componentes da plataforma
```

Os componentes de Registry, Lifecycle, Validation, Query e Administration oferecem suporte transversal a toda essa cadeia.

---

# Princípios Arquiteturais

Os componentes seguem os princípios de:

- responsabilidade única;
- baixo acoplamento;
- alta coesão;
- composição por serviços;
- reutilização institucional;
- rastreabilidade completa;
- integração desacoplada.

---

# Resultado Esperado

Ao final desta arquitetura, o Tenant Management possuirá um conjunto de componentes especializados que atuarão de forma integrada para administrar organizações, tenants, ambientes e contexto organizacional, tornando-se a base oficial da infraestrutura multi-tenant da Deja Platform.