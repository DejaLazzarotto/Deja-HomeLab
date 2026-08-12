# 11. Integração com Security

## Objetivo

Esta seção define a integração institucional entre o Tenant Management e o componente Security da Deja Platform.

O objetivo é garantir que a identidade organizacional resolvida pelo Tenant Management seja utilizada pelo Security para aplicação das políticas de autenticação, autorização e controle de acesso, preservando isolamento e consistência em toda a plataforma.

---

# Princípio de Integração

Tenant Management e Security possuem responsabilidades distintas e complementares.

O Tenant Management identifica o contexto organizacional da operação.

O Security valida a identidade do solicitante e determina quais ações podem ser executadas dentro desse contexto.

Nenhum dos componentes substitui as responsabilidades do outro.

---

# Responsabilidades do Tenant Management

Compete ao Tenant Management:

- resolver o Tenant Context;
- identificar Organização;
- identificar Tenant;
- identificar Ambiente;
- fornecer o contexto organizacional aos consumidores;
- preservar os limites estruturais entre Organizações, Tenants e Ambientes;
- impedir operações fora do escopo institucional autorizado.

O Tenant Management não autentica usuários nem concede permissões.

---

# Responsabilidades do Security

Compete ao Security:

- autenticar identidades;
- autorizar operações;
- validar credenciais;
- aplicar políticas de acesso;
- administrar perfis e permissões;
- emitir decisões de autorização.

O Security utiliza o Tenant Context como referência para aplicar suas políticas.

---

# Fluxo de Integração

A interação entre os componentes segue o fluxo institucional abaixo:

```text
Solicitação
      │
      ▼
Security
(Autenticação)
      │
      ▼
Tenant Context Resolver
      │
      ▼
Tenant Context
      │
      ▼
Security
(Autorização)
      │
      ▼
Execução da Operação
```

Esse fluxo assegura que toda decisão de segurança considere o contexto organizacional correto.

---

# Contexto Organizacional

O Tenant Context fornece ao Security informações como:

- identificador da Organização;
- identificador do Tenant;
- identificador do Ambiente;
- versão do contexto;
- identificador da execução.

Essas informações são utilizadas exclusivamente para aplicação das políticas de segurança.

---

# Papéis Institucionais

A Gestão Institucional utiliza os seguintes papéis:

## Platform Admin

O `platform_admin` representa uma identidade administrativa interna da Deja Platform.

Esse papel:

- não pertence a uma Organização cliente;
- não pertence a um Tenant;
- não pertence a um Ambiente;
- possui alcance institucional global;
- provisiona e administra Organizações;
- administra Tenants e Ambientes;
- executa operações estruturais reservadas à plataforma.

O papel deve ser concedido somente a identidades internas controladas e auditáveis.

## Organization Admin

O `organization_admin` representa o administrador de uma Organização cliente.

Esse papel:

- pertence obrigatoriamente a uma Organização;
- não pertence a um Tenant;
- não pertence a um Ambiente;
- consulta e atualiza somente a própria Organização;
- administra Tenants e Ambientes pertencentes à própria Organização;
- não cria nem exclui Organizações;
- não acessa recursos de outras Organizações.

## Tenant Admin

O `tenant_admin` representa o administrador de um Tenant.

Esse papel:

- pertence obrigatoriamente a uma Organização e a um Tenant;
- não pertence a um Ambiente;
- consulta somente a própria Organização;
- consulta e atualiza somente o próprio Tenant;
- administra Ambientes pertencentes ao próprio Tenant;
- não cria nem exclui Tenants;
- não acessa outros Tenants ou Organizações.

## Manager

O `manager` representa um gestor operacional.

Esse papel:

- pertence obrigatoriamente a uma Organização, a um Tenant e a um Ambiente;
- possui acesso somente de consulta à própria Organização;
- possui acesso somente de consulta ao próprio Tenant;
- possui acesso somente de consulta ao próprio Ambiente;
- não executa operações estruturais de criação, atualização ou exclusão.

## Analyst e Viewer

Os papéis `analyst` e `viewer` não possuem acesso direto às rotas administrativas da Gestão Institucional.

O acesso funcional desses papéis deve ocorrer pelas capacidades de negócio autorizadas para seus respectivos contextos.

---

# Matriz de Permissões

## Organizações

| Operação | platform_admin | organization_admin | tenant_admin | manager | analyst | viewer |
|---|---:|---:|---:|---:|---:|---:|
| Listar | Global | Própria | Própria | Própria | Negado | Negado |
| Consultar | Global | Própria | Própria | Própria | Negado | Negado |
| Criar | Permitido | Negado | Negado | Negado | Negado | Negado |
| Atualizar | Global | Própria | Negado | Negado | Negado | Negado |
| Excluir | Permitido | Negado | Negado | Negado | Negado | Negado |

## Tenants

| Operação | platform_admin | organization_admin | tenant_admin | manager | analyst | viewer |
|---|---:|---:|---:|---:|---:|---:|
| Listar | Global | Própria organização | Próprio | Próprio | Negado | Negado |
| Consultar | Global | Própria organização | Próprio | Próprio | Negado | Negado |
| Criar | Permitido | Própria organização | Negado | Negado | Negado | Negado |
| Atualizar | Global | Própria organização | Próprio | Negado | Negado | Negado |
| Excluir | Permitido | Própria organização | Negado | Negado | Negado | Negado |

## Ambientes

| Operação | platform_admin | organization_admin | tenant_admin | manager | analyst | viewer |
|---|---:|---:|---:|---:|---:|---:|
| Listar | Global | Própria organização | Próprio tenant | Próprio | Negado | Negado |
| Consultar | Global | Própria organização | Próprio tenant | Próprio | Negado | Negado |
| Criar | Permitido | Própria organização | Próprio tenant | Negado | Negado | Negado |
| Atualizar | Global | Própria organização | Próprio tenant | Negado | Negado | Negado |
| Excluir | Permitido | Própria organização | Próprio tenant | Negado | Negado | Negado |

---

# Regras de Escopo

Toda operação protegida deve avaliar simultaneamente o papel e o escopo institucional da identidade.

As seguintes regras são obrigatórias:

- `platform_admin` opera sem vínculo com Organização, Tenant ou Ambiente;
- `organization_admin` permanece limitado à Organização presente em sua identidade autenticada;
- `tenant_admin` permanece limitado à Organização e ao Tenant presentes em sua identidade autenticada;
- `manager` permanece limitado à Organização, ao Tenant e ao Ambiente presentes em sua identidade autenticada;
- filtros de listagem não podem ampliar o escopo da identidade;
- tentativas de acesso cruzado devem ser negadas;
- payloads de criação e atualização devem permanecer dentro do escopo autorizado;
- a autorização deve ser aplicada nas rotas e novamente na camada de serviço;
- a ausência de autenticação deve produzir erro de autenticação;
- papel ou escopo insuficiente deve produzir erro de autorização.

Uma listagem autorizada nunca deve retornar recursos externos ao escopo efetivo da identidade.

---

# Controle de Acesso

As permissões concedidas pelo Security devem ser avaliadas sempre dentro do Tenant Context ativo.

Privilégios administrativos de clientes não concedem alcance global.

Somente o `platform_admin` pode executar operações entre Organizações distintas, e toda utilização desse papel deve ser explicitamente autenticada e auditada.

O acesso entre Tenants distintos depende do papel, do escopo institucional e das políticas vigentes.

---

# Provisionamento

Durante o provisionamento de novas Organizações, Tenants ou Ambientes, o Tenant Management aciona os processos necessários para que o Security inicialize:

- políticas padrão;
- administradores iniciais;
- papéis institucionais;
- estruturas de autorização.

A criação e a exclusão de Organizações são operações reservadas ao `platform_admin`.

Após a criação de uma Organização, deve ser possível associar seu primeiro `organization_admin` sem conceder a esse usuário privilégios globais.

A implementação dos mecanismos de identidade e autorização permanece sob responsabilidade do Security.

---

# Defesa em Profundidade

A autorização da Gestão Institucional deve ser aplicada em mais de uma camada.

As rotas devem:

- exigir Bearer token;
- validar os papéis permitidos;
- rejeitar operações não autorizadas antes da execução funcional.

Os serviços devem:

- repetir as validações de papel;
- validar o escopo do recurso encontrado;
- validar o escopo dos dados recebidos;
- aplicar escopo obrigatório às listagens.

Essa duplicação intencional evita que chamadas internas ou futuras integrações contornem as políticas aplicadas na camada HTTP.

---

# Auditoria

Eventos relevantes da integração devem produzir registros institucionais, incluindo:

- resolução de contexto;
- validações de acesso;
- acessos globais de `platform_admin`;
- falhas de autorização;
- tentativas de acesso cruzado;
- mudanças estruturais;
- provisionamentos.

Os registros são encaminhados aos componentes de auditoria e observabilidade da plataforma.

---

# Resiliência

Caso o Security não consiga autenticar ou autorizar uma operação, o processamento deverá ser interrompido antes da execução funcional.

Da mesma forma, se o Tenant Context não puder ser resolvido, nenhuma decisão de autorização poderá ser emitida.

Essa dependência garante integridade e previsibilidade operacional.

---

# Benefícios

A integração entre Tenant Management e Security proporciona:

- autenticação contextualizada;
- autorização consistente;
- isolamento entre Tenants;
- segregação entre administração da plataforma e administração de clientes;
- aplicação uniforme das políticas de acesso;
- rastreabilidade completa;
- redução de riscos de acesso indevido;
- alinhamento entre identidade e contexto organizacional.

---

# Resultado Esperado

Ao final desta definição, o Tenant Management e o Security atuam de forma integrada e complementar, garantindo que toda operação executada na Deja Platform esteja simultaneamente associada a um contexto institucional válido e submetida às políticas de autenticação, papel e escopo da Deja Platform.