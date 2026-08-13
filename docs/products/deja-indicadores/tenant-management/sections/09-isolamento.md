# 9. Isolamento

## Objetivo

Esta seção define as políticas institucionais de isolamento adotadas pela Deja Platform para garantir que Organizações, Tenants e Ambientes operem de forma completamente independente, preservando segurança, integridade, confidencialidade e governança.

O isolamento constitui um dos princípios fundamentais da arquitetura multi-tenant da plataforma.

---

# Princípio Fundamental

O Tenant é a unidade oficial de isolamento da Deja Platform.

Todo recurso institucional pertence obrigatoriamente a um único Tenant e somente poderá ser acessado dentro de um Contexto de Execução válido.

O isolamento é aplicado por projeto arquitetural e não apenas por configuração.

---

# Níveis de Isolamento

A arquitetura estabelece os seguintes níveis de isolamento:

- organizacional;
- operacional;
- funcional;
- informacional;
- observacional;
- administrativo.

Cada nível atua de forma complementar para assegurar independência entre clientes.

---

# Isolamento Organizacional

Cada Organização administra exclusivamente seus próprios Tenants.

Não existe compartilhamento administrativo entre Organizações, salvo quando explicitamente previsto por mecanismos institucionais de delegação.

Todas as operações são restritas ao domínio organizacional correspondente.

---

# Isolamento entre Tenants

Os Tenants são completamente independentes entre si.

Cada Tenant possui:

- identidade própria;
- configurações próprias;
- ambientes próprios;
- recursos próprios;
- histórico próprio;
- eventos próprios;
- métricas próprias;
- logs próprios.

Nenhuma operação pode acessar recursos pertencentes a outro Tenant sem autorização institucional explícita.

---

# Isolamento entre Ambientes

Os Ambientes de um mesmo Tenant também permanecem isolados.

Development, Homologation, Production e Sandbox são tratados como domínios operacionais independentes.

Essa separação evita contaminação entre diferentes estágios do ciclo de vida das aplicações.

---

# Isolamento da Gestão de Empresas

Toda empresa cadastrada na Deja Indicadores pertence obrigatoriamente a um único Ambiente.

O Ambiente constitui o vínculo persistente direto da empresa. O Tenant e a Organização proprietários são determinados pela hierarquia institucional do Ambiente, evitando duplicidade de identificadores e combinações inconsistentes de escopo.

A Gestão de Empresas deve respeitar as seguintes regras de isolamento:

- empresas sem Ambiente não podem existir;
- uma empresa não pode pertencer simultaneamente a mais de um Ambiente;
- listagens devem aplicar filtros institucionais derivados da identidade autenticada;
- consultas individuais devem validar a hierarquia real da empresa antes de retornar seus dados;
- criações e atualizações devem resolver o Ambiente informado e validar seu Tenant e sua Organização;
- operações entre Organizações, Tenants ou Ambientes distintos devem ser negadas quando excederem o escopo da identidade;
- referências indiretas por indicadores, medições, dashboards ou relatórios não podem ampliar o acesso à empresa;
- somente identidades com alcance global autorizado podem operar empresas entre diferentes Organizações;
- o isolamento deve ser repetido nas camadas de entrada, serviço e persistência.

A associação direta ao Ambiente preserva simultaneamente o isolamento operacional entre ambientes e o isolamento institucional entre tenants e organizações.

# Isolamento da Gestão de Indicadores

Todo indicador cadastrado na Deja Indicadores pertence obrigatoriamente a uma única empresa.

A empresa constitui o vínculo persistente direto do indicador. O Ambiente, o Tenant e a Organização proprietários são determinados pela hierarquia institucional da empresa, evitando colunas redundantes e combinações inconsistentes de escopo.

A Gestão de Indicadores deve respeitar as seguintes regras de isolamento:

- indicadores sem empresa não podem existir;
- um indicador não pode pertencer simultaneamente a mais de uma empresa;
- `organization_id`, `tenant_id` e `environment_id` não devem ser duplicados no indicador;
- listagens devem aplicar filtros institucionais derivados da identidade autenticada;
- filtros explícitos por empresa, Organização, Tenant ou Ambiente não podem ampliar o escopo autenticado;
- consultas individuais devem resolver a empresa e validar sua hierarquia real antes de retornar o indicador;
- criações devem validar a empresa informada e toda a sua hierarquia institucional;
- atualizações devem validar tanto a empresa atual quanto a empresa de destino;
- transferências entre empresas devem ser negadas quando a origem ou o destino exceder o escopo da identidade;
- exclusões devem validar o escopo da empresa antes de avaliar dependências funcionais;
- referências indiretas por medições, dashboards ou relatórios não podem ampliar o acesso ao indicador;
- somente identidades com alcance global autorizado podem operar indicadores entre diferentes Organizações;
- o isolamento deve ser repetido nas camadas de entrada, serviço e persistência.

A associação direta à empresa preserva o modelo de domínio e herda integralmente o isolamento operacional entre Ambientes e o isolamento institucional entre Tenants e Organizações.

---

# Isolamento de Dados

Todo dado institucional deverá estar associado ao Tenant correspondente.

A arquitetura permite diferentes estratégias físicas de armazenamento, incluindo:

- banco compartilhado;
- banco dedicado;
- esquema dedicado;
- armazenamento distribuído.

Independentemente da implementação física, o isolamento lógico permanece obrigatório.

---

# Isolamento de Configuração

As configurações são segregadas por Tenant e, quando aplicável, por Ambiente.

Um Tenant não possui acesso às configurações pertencentes a outro Tenant.

A gestão dessas configurações permanece sob responsabilidade do componente Configuration.

---

# Isolamento de Segurança

O Tenant Management não implementa mecanismos de autenticação ou autorização.

Entretanto, todas as políticas de segurança deverão respeitar o contexto organizacional resolvido.

A autenticação é realizada pelo componente Security, que utiliza o Tenant Context como referência para aplicação das políticas de acesso.

---

# Isolamento de Observabilidade

Métricas, logs, traces e eventos deverão permanecer segregados por Tenant.

Essa separação garante:

- monitoramento independente;
- auditoria consistente;
- diagnósticos precisos;
- conformidade regulatória.

A responsabilidade pela implementação permanece no componente Observability.

---

# Isolamento Administrativo

Administradores organizacionais operam exclusivamente dentro do escopo autorizado.

Ferramentas administrativas devem respeitar os limites definidos pelo Tenant Context.

Operações globais somente poderão ser executadas por componentes institucionais autorizados.

---

# Compartilhamento Controlado

Em situações específicas, recursos poderão ser compartilhados entre Tenants.

Esse compartilhamento deverá:

- ser explicitamente previsto pela arquitetura;
- utilizar mecanismos institucionais;
- preservar rastreabilidade;
- registrar auditoria;
- respeitar as políticas de segurança.

O compartilhamento implícito é proibido.

---

# Benefícios

A política institucional de isolamento proporciona:

- segurança;
- confidencialidade;
- previsibilidade operacional;
- governança;
- conformidade;
- escalabilidade;
- reutilização segura da infraestrutura;
- preparação para operação SaaS em larga escala.

---

# Resultado Esperado

Ao final desta definição, toda a Deja Platform passa a operar sobre um modelo institucional de isolamento que garante independência entre Organizações, Tenants e Ambientes, preservando a integridade dos recursos compartilhados e sustentando uma arquitetura multi-tenant segura, escalável e governável.