# 08. Administração de Usuários

## Visão Geral

A Administration Platform fornece a camada institucional responsável pela administração operacional dos usuários com funções administrativas e operacionais na Deja Platform.

A autenticação, autorização, gestão de identidades e controle de acesso permanecem sob responsabilidade exclusiva do componente Security. A Administration Platform coordena essas operações por meio dos contratos oficiais, oferecendo uma interface administrativa unificada para gestão de usuários.

---

## Objetivos

A Administração de Usuários possui os seguintes objetivos:

- centralizar a gestão operacional das identidades humanas;
- padronizar processos de administração de usuários;
- garantir aplicação consistente das políticas de acesso;
- facilitar a delegação de responsabilidades;
- assegurar rastreabilidade das alterações;
- preservar a separação entre administração e segurança;
- suportar o provisionamento inicial de Organizações;
- impedir elevação indevida de privilégios;
- preservar o isolamento entre Organizações e Tenants.

---

## Papéis Administradores

A capacidade reconhece três papéis com permissões administrativas:

### Platform Admin

O `platform_admin` administra identidades em alcance global.

Compete a esse papel:

- listar e consultar usuários de qualquer escopo;
- cadastrar outros administradores da plataforma;
- cadastrar o primeiro `organization_admin` de uma Organização;
- administrar usuários de qualquer Organização, Tenant ou Ambiente;
- definir ou redefinir senhas;
- ativar e desativar acessos;
- alterar papéis e vínculos institucionais.

Toda operação global deve ser auditável.

### Organization Admin

O `organization_admin` administra usuários somente da própria Organização.

Compete a esse papel:

- listar e consultar usuários da própria Organização;
- cadastrar usuários vinculados à própria Organização;
- administrar usuários de todos os Tenants e Ambientes da própria Organização;
- definir ou redefinir senhas;
- ativar e desativar acessos.

Esse papel não pode:

- administrar usuários de outras Organizações;
- criar ou administrar `platform_admin`;
- mover usuários para outra Organização;
- atribuir alcance global.

### Tenant Admin

O `tenant_admin` administra usuários somente do próprio Tenant.

Compete a esse papel:

- listar e consultar usuários do próprio Tenant;
- cadastrar usuários vinculados ao próprio Tenant;
- administrar usuários dos Ambientes pertencentes ao próprio Tenant;
- definir ou redefinir senhas;
- ativar e desativar acessos.

Esse papel não pode:

- administrar `platform_admin`;
- administrar `organization_admin`;
- acessar usuários de outro Tenant;
- mover usuários para outro Tenant;
- atribuir papel com alcance superior ao próprio.

---

## Papéis Não Administradores

Os papéis abaixo não possuem acesso à Administração de Usuários:

- `manager`;
- `analyst`;
- `viewer`.

Esses papéis utilizam apenas as capacidades funcionais expressamente autorizadas para seus respectivos contextos.

---

## Matriz de Permissões

| Operação | platform_admin | organization_admin | tenant_admin | manager | analyst | viewer |
|---|---:|---:|---:|---:|---:|---:|
| Listar usuários | Global | Própria organização | Próprio tenant | Negado | Negado | Negado |
| Consultar usuário | Global | Própria organização | Próprio tenant | Negado | Negado | Negado |
| Criar platform_admin | Permitido | Negado | Negado | Negado | Negado | Negado |
| Criar organization_admin | Permitido | Própria organização | Negado | Negado | Negado | Negado |
| Criar demais papéis | Global | Própria organização | Próprio tenant | Negado | Negado | Negado |
| Atualizar usuário | Global | Própria organização | Próprio tenant | Negado | Negado | Negado |
| Definir senha | Global | Própria organização | Próprio tenant | Negado | Negado | Negado |

A permissão indicada na matriz não elimina a validação dos vínculos obrigatórios de cada papel.

---

## Regras de Escopo

As operações devem aplicar as seguintes regras:

- `platform_admin` não possui vínculo com Organização, Tenant ou Ambiente;
- `organization_admin` pertence a uma Organização e não possui Tenant nem Ambiente;
- `tenant_admin` pertence a uma Organização e a um Tenant, sem Ambiente;
- `manager`, `analyst` e `viewer` pertencem a uma Organização, a um Tenant e a um Ambiente;
- o Tenant informado deve pertencer à Organização;
- o Ambiente informado deve pertencer ao Tenant;
- filtros de listagem não podem ampliar o escopo do administrador;
- dados de criação e atualização não podem ampliar o escopo do administrador;
- tentativas de acesso cruzado devem ser negadas.

---

## Provisionamento Inicial

A criação de uma nova Organização é realizada por um `platform_admin`.

Após a criação da Organização, o mesmo administrador global pode cadastrar seu primeiro `organization_admin`.

A partir desse ponto, o `organization_admin` pode administrar os usuários, Tenants e Ambientes pertencentes à própria Organização, conforme as políticas de cada capacidade.

A criação do primeiro `platform_admin` não deve ocorrer por cadastro público. Ela depende de um procedimento seguro de inicialização da plataforma, executado de forma controlada e auditável.

---

## Operações Administrativas

As principais operações incluem:

- cadastro de administradores;
- cadastro de usuários operacionais;
- consulta de usuários;
- atualização de informações;
- associação e alteração de papéis;
- ativação e desativação de acessos;
- definição e redefinição de senhas;
- delegação de responsabilidades;
- consulta de permissões efetivas;
- revogação de privilégios administrativos.

Toda operação depende de autenticação válida e autorização adequada.

---

## Fluxo Operacional

O processo administrativo segue o fluxo institucional:

```text
Administrador
        │
        ▼
Administration Platform
        │
        ▼
Validação de Contexto
        │
        ▼
Security
        │
        ▼
Validação de Permissões
        │
        ▼
Execução da Operação
        │
        ▼
Registro de Auditoria
```

Esse fluxo garante que nenhuma alteração de acesso ocorra fora do domínio oficial de Security.

---

## Defesa em Profundidade

A Administração de Usuários deve aplicar autorização em mais de uma camada.

As rotas devem:

- exigir Bearer token;
- validar o papel administrativo;
- rejeitar identidades sem permissão.

Os serviços devem:

- repetir a validação do papel;
- aplicar escopo obrigatório às listagens;
- validar o usuário-alvo;
- validar os dados recebidos;
- impedir elevação indevida;
- impedir movimentação institucional não autorizada.

---

## Princípios Operacionais

A Administração de Usuários observa os seguintes princípios:

- menor privilégio;
- segregação de funções;
- autenticação obrigatória;
- autorização centralizada;
- defesa em profundidade;
- auditoria completa;
- consistência institucional;
- rastreabilidade integral.

---

## Integração Institucional

A Administration Platform não mantém identidade, credenciais ou políticas de autorização.

Toda validação de autenticação, autorização, perfis, papéis e permissões é realizada exclusivamente pelo componente Security.

A Administration Platform atua como camada de coordenação administrativa, preservando a independência do domínio de segurança e oferecendo uma experiência operacional integrada para os administradores da Deja Platform.