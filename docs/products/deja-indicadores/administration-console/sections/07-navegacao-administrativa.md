# 07. Navegação Administrativa

## Objetivo

Definir a arquitetura da navegação administrativa da Administration Console, estabelecendo como administradores acessam, descobrem e transitam entre as capacidades institucionais da Deja Platform de maneira consistente, eficiente e escalável.

---

## Princípios da Navegação

A navegação administrativa deve ser:

- consistente;
- previsível;
- contextual;
- orientada por capacidades;
- extensível;
- responsiva;
- segura.

Toda organização da interface deve refletir a arquitetura institucional da plataforma.

---

## Estrutura Hierárquica

A navegação é organizada em níveis bem definidos.

### Nível 1 — Shell Administrativo

Disponibiliza os elementos permanentes da interface:

- menu principal;
- cabeçalho;
- barra de contexto;
- notificações;
- acesso ao perfil;
- pesquisa global.

---

### Nível 2 — Capacidades Institucionais

Cada capacidade administrativa possui uma entrada própria na navegação.

Exemplos:

- Dashboard;
- Organizações;
- Tenants;
- Usuários;
- Billing & Licensing;
- Marketplace;
- Security;
- Configuration;
- Observability;
- API Management;
- Developer Portal.

---

### Nível 3 — Consoles Especializados

Cada capacidade pode disponibilizar consoles específicos para suas operações.

Exemplos:

- gestão;
- configurações;
- auditoria;
- monitoramento;
- relatórios;
- diagnósticos;
- operações.

---

## Navegação Contextual

A Console mantém contexto durante toda a sessão administrativa.

Entre as informações preservadas estão:

- organização ativa;
- tenant ativo;
- usuário autenticado;
- permissões;
- ambiente selecionado;
- filtros ativos.

A mudança de contexto deve ocorrer de forma explícita e auditável.

---

## Recursos de Navegação

A arquitetura prevê suporte institucional para:

- breadcrumbs;
- favoritos;
- histórico recente;
- pesquisa global;
- atalhos rápidos;
- menus contextuais;
- navegação por comandos;
- deep links.

---

## Descoberta de Funcionalidades

Novos módulos administrativos podem ser incorporados automaticamente à navegação institucional por meio de registros públicos, preservando baixo acoplamento e evitando alterações estruturais no Shell Administrativo.

---

## Segurança da Navegação

A exibição de menus, páginas e funcionalidades respeita integralmente as permissões concedidas ao usuário autenticado.

Recursos não autorizados não devem ser apresentados na interface.

---

## Evolução

A arquitetura da navegação foi projetada para permitir crescimento contínuo da plataforma, mantendo uma experiência uniforme mesmo com a incorporação de novas capacidades administrativas.