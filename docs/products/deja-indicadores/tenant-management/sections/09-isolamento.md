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

# Isolamento da Gestão de Medições

Toda medição cadastrada na Deja Indicadores pertence obrigatoriamente a um único indicador.

O indicador constitui o vínculo persistente direto da medição. A empresa, o Ambiente, o Tenant e a Organização proprietários são determinados pela hierarquia institucional do indicador, evitando colunas redundantes e combinações inconsistentes de escopo.

A hierarquia institucional da medição é:

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

A Gestão de Medições deve respeitar as seguintes regras de isolamento:

- medições sem indicador não podem existir;
- uma medição não pode pertencer simultaneamente a mais de um indicador;
- `company_id`, `organization_id`, `tenant_id` e `environment_id` não devem ser duplicados na medição;
- listagens devem aplicar filtros institucionais derivados da identidade autenticada;
- filtros explícitos por empresa, indicador, Organização, Tenant ou Ambiente não podem ampliar o escopo autenticado;
- filtros por período devem ser combinados com o escopo institucional obrigatório;
- consultas individuais devem resolver o indicador, a empresa e a hierarquia real antes de retornar a medição;
- criações devem validar o indicador informado e toda a sua hierarquia institucional;
- atualizações devem validar tanto o indicador atual quanto o indicador de destino;
- transferências entre indicadores devem ser negadas quando a origem ou o destino exceder o escopo da identidade;
- exclusões devem validar a hierarquia institucional antes de remover a medição;
- o autor autenticado da criação deve ser registrado sem alterar o vínculo institucional do recurso;
- referências indiretas por dashboards ou relatórios não podem ampliar o acesso à medição;
- somente identidades com alcance global autorizado podem operar medições entre diferentes Organizações;
- o isolamento deve ser repetido nas camadas de entrada, serviço e persistência.

A associação direta ao indicador preserva o modelo de domínio e herda integralmente o isolamento da empresa, dos Ambientes, dos Tenants e das Organizações.

---

# Isolamento dos Dashboards

Os Dashboards da Deja Indicadores não constituem uma nova unidade de propriedade institucional. Eles consolidam empresas, indicadores e medições cujo escopo é herdado da hierarquia persistente desses recursos.

A resolução institucional utilizada nas agregações é:

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

Os Dashboards devem respeitar as seguintes regras de isolamento:

- toda consulta exige identidade autenticada e papel de leitura permitido;
- `platform_admin` pode consultar agregações globais;
- `organization_admin` recebe somente dados da própria Organização;
- `tenant_admin` recebe somente dados do próprio Tenant;
- `manager`, `analyst` e `viewer` recebem somente dados do próprio Ambiente;
- filtros de Organização, Tenant, Ambiente, empresa e indicador não podem ampliar o escopo autenticado;
- filtros por período devem ser combinados com o escopo institucional obrigatório;
- contagens de empresas, indicadores e medições devem utilizar o mesmo recorte institucional;
- agrupamentos por status devem excluir integralmente recursos fora do escopo;
- indicadores, medições atuais, percentuais de atingimento, situações e históricos devem ser calculados somente com dados autorizados;
- um dashboard vazio dentro do escopo não pode incorporar dados existentes em outro Ambiente, Tenant ou Organização;
- consultas persistentes devem aplicar junções e filtros institucionais antes da materialização dos resultados;
- o carregamento global seguido de filtragem apenas em memória é proibido;
- filtros por empresa ou indicador devem validar a hierarquia institucional real do recurso;
- filtros válidos, porém sem correspondência entre empresa e indicador, devem produzir agregações vazias;
- relatórios e outros consumidores internos devem propagar a identidade autenticada ao dashboard;
- nenhum consumidor interno pode utilizar o dashboard como caminho alternativo para contornar o isolamento;
- o isolamento deve ser repetido nas camadas de entrada, serviço e persistência.

A aplicação uniforme do escopo em todas as consultas impede que totais, KPIs, agrupamentos ou históricos misturem dados pertencentes a domínios institucionais distintos.

---

# Isolamento dos Relatórios

Os Relatórios da Deja Indicadores não constituem uma nova unidade de propriedade institucional nem mantêm um escopo paralelo. Eles reutilizam as agregações protegidas dos Dashboards e herdam integralmente o isolamento das empresas, dos indicadores e das medições consolidados.

Os Relatórios devem respeitar as seguintes regras de isolamento:

- toda consulta exige identidade autenticada e papel de leitura permitido;
- `platform_admin` pode consultar relatórios globais;
- `organization_admin` recebe somente dados da própria Organização;
- `tenant_admin` recebe somente dados do próprio Tenant;
- `manager`, `analyst` e `viewer` recebem somente dados do próprio Ambiente;
- a identidade autenticada deve ser propagada da rota para o serviço de relatórios e deste para o serviço de dashboard;
- filtros de Organização, Tenant, Ambiente, empresa e indicador não podem ampliar o escopo autenticado;
- filtros por período devem ser combinados com o escopo institucional obrigatório;
- filtros institucionais compatíveis podem restringir adicionalmente o resultado;
- filtros por empresas ou indicadores existentes fora do escopo devem ser negados;
- recursos inexistentes devem preservar a semântica funcional de recurso não encontrado;
- empresa e indicador autorizados, mas sem relação entre si, devem produzir relatório vazio;
- um relatório vazio dentro do escopo não pode incorporar dados existentes em outro Ambiente, Tenant ou Organização;
- totais, agrupamentos, indicadores, medições atuais, percentuais de atingimento, situações e históricos devem utilizar exatamente o mesmo recorte institucional do dashboard;
- os metadados devem registrar os filtros explicitamente solicitados, sem apresentar filtros institucionais implícitos como parâmetros enviados pelo consumidor;
- consultas persistentes reutilizadas pelo relatório devem aplicar junções e filtros institucionais antes da materialização dos resultados;
- o carregamento global seguido de filtragem apenas em memória é proibido;
- nenhuma chamada interna pode omitir a identidade autenticada ou utilizar o relatório como caminho alternativo para contornar o isolamento;
- o isolamento deve ser repetido na entrada HTTP, no serviço de relatórios, no serviço de dashboard e na persistência.

A reutilização do Dashboard protegido garante que relatórios não misturem dados pertencentes a Organizações, Tenants ou Ambientes distintos e evita a duplicação de regras institucionais de consulta.

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