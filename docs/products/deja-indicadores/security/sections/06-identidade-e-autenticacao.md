# 06. Identidade e Autenticação

## Objetivo

Esta seção descreve a arquitetura institucional de identidade e autenticação do Security da Deja Platform.

A identidade representa a base fundamental do modelo de segurança, permitindo identificar usuários, serviços, componentes e agentes antes da realização de qualquer operação protegida.

A autenticação garante que a identidade apresentada seja validada antes da concessão de acesso.

---

# Identidade

## Conceito

Uma identidade representa uma entidade reconhecida pela Deja Platform.

Toda entidade que interage com recursos protegidos deve possuir uma identidade única e rastreável.

---

## Tipos de identidade

O modelo suporta diferentes categorias:

### Identidade humana

Representa usuários da plataforma.

Exemplos:

- administradores da plataforma;
- administradores de organizações;
- administradores de tenants;
- gestores;
- analistas;
- usuários de consulta.

### Identidade de serviço

Representa serviços e aplicações que executam operações automaticamente.

Exemplos:

- APIs;
- workers;
- serviços internos;
- integrações.

### Identidade de componente

Representa componentes arquiteturais da plataforma.

Exemplos:

- Execution Engine;
- Workflow Engine;
- Intelligence Core;
- Workspace Runtime.

### Identidade de agente

Representa agentes inteligentes capazes de executar ações.

Exemplos:

- AI Assistant;
- agentes especializados;
- automações inteligentes.

---

# Modelo de Identidade

Uma identidade pode possuir:

- identificador único;
- tipo;
- atributos;
- papel institucional;
- Organização associada;
- Tenant associado;
- Ambiente associado;
- permissões relacionadas;
- estado operacional;
- histórico de atividades.

Os vínculos com Organização, Tenant e Ambiente são opcionais no modelo geral, mas sua obrigatoriedade depende do papel institucional da identidade.

---

# Escopos de Identidade Humana

As identidades humanas administrativas e operacionais seguem os seguintes escopos:

## Identidade Global

A identidade com papel `platform_admin` representa um administrador interno da Deja Platform.

Ela não possui vínculo com Organização, Tenant ou Ambiente.

A ausência desses vínculos é obrigatória e representa alcance global controlado, não ausência de validação.

## Identidade Organizacional

A identidade com papel `organization_admin` pertence obrigatoriamente a uma Organização.

Ela não pode possuir vínculo com Tenant nem Ambiente.

## Identidade de Tenant

A identidade com papel `tenant_admin` pertence obrigatoriamente a uma Organização e a um Tenant.

Ela não pode possuir vínculo com Ambiente.

## Identidade de Ambiente

As identidades com papéis `manager`, `analyst` e `viewer` pertencem obrigatoriamente a uma Organização, a um Tenant e a um Ambiente.

---

# Regras de Consistência

Toda identidade humana deve respeitar as seguintes regras:

| Papel | Organização | Tenant | Ambiente |
|---|---:|---:|---:|
| `platform_admin` | Proibida | Proibido | Proibido |
| `organization_admin` | Obrigatória | Proibido | Proibido |
| `tenant_admin` | Obrigatória | Obrigatório | Proibido |
| `manager` | Obrigatória | Obrigatório | Obrigatório |
| `analyst` | Obrigatória | Obrigatório | Obrigatório |
| `viewer` | Obrigatória | Obrigatório | Obrigatório |

Além da presença dos vínculos:

- o Tenant deve pertencer à Organização informada;
- o Ambiente deve pertencer ao Tenant informado;
- papéis globais não podem receber escopo de cliente;
- papéis institucionais não podem operar fora do escopo presente na identidade autenticada.

Identidades inconsistentes devem ser rejeitadas antes de sua ativação.

---

# Ciclo de Vida da Identidade

O ciclo de vida contempla:

```text
Created
   ↓
Activated
   ↓
Used
   ↓
Suspended
   ↓
Revoked
   ↓
Archived
```

Cada transição deve ser controlada e auditável.

---

# Authentication Service

## Responsabilidade

O Authentication Service valida a identidade apresentada por uma entidade.

A autenticação ocorre antes de qualquer operação que exija proteção.

---

## Métodos de Autenticação

A arquitetura suporta diferentes mecanismos:

- autenticação por credenciais;
- tokens;
- certificados;
- chaves de serviço;
- provedores externos de identidade.

---

# Contexto Autenticado

Após uma autenticação bem-sucedida, o Security disponibiliza o contexto necessário para autorização.

Para identidades humanas, o contexto autenticado deve incluir:

- identificador da identidade;
- papel institucional;
- identificador da Organização, quando aplicável;
- identificador do Tenant, quando aplicável;
- identificador do Ambiente, quando aplicável;
- estado da identidade.

O contexto autenticado deve refletir os vínculos persistidos da identidade e não pode aceitar escopo fornecido livremente pelo cliente.

---

# Sessões e Contexto

Após uma autenticação bem-sucedida, o Security mantém informações de contexto.

O contexto pode incluir:

- identidade autenticada;
- momento da autenticação;
- origem da solicitação;
- recursos solicitados;
- nível de confiança.

---

# Autenticação de Serviços

Serviços internos e externos devem possuir mecanismos próprios de autenticação.

Nenhum serviço deve assumir confiança automática por estar dentro da plataforma.

---

# Integração com Autorização

A autenticação responde:

> Quem está solicitando a operação?

A autorização responde:

> Essa identidade pode executar essa operação?

As responsabilidades permanecem separadas.

Fluxo:

```text
Identity
   ↓
Authentication
   ↓
Authorization
   ↓
Execution
```

---

# Segurança de Identidade

O Security deve proteger:

- informações de identidade;
- credenciais;
- tokens;
- certificados;
- atributos sensíveis.

Papéis de alcance global exigem controles adicionais, incluindo:

- concessão restrita;
- credenciais individualizadas;
- rastreabilidade completa;
- revisão periódica;
- revogação imediata quando necessária.

---

# Auditoria

Eventos relacionados à identidade e autenticação devem ser registrados.

Exemplos:

- criação de identidade;
- autenticação realizada;
- falha de autenticação;
- alteração de papel;
- alteração de escopo;
- alteração de atributos;
- revogação de acesso.

A autenticação de uma identidade `platform_admin` deve ser identificável nos registros de auditoria.

---

# Integração Institucional

A identidade e autenticação são utilizadas por:

- Execution Engine;
- Workflow Engine;
- Intelligence Core;
- Execution Log;
- Execution History;
- Observability;
- Data Pipeline;
- Workspace;
- APIs.

---

# Benefícios Arquiteturais

Este modelo proporciona:

- identificação confiável;
- separação entre identidades globais e identidades de clientes;
- controle centralizado;
- rastreabilidade completa;
- suporte a múltiplos tipos de entidades;
- evolução para ambientes corporativos distribuídos.