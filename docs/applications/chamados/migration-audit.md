# Auditoria da migração — Chamados-PWA → Deja Platform

## Objetivo

Registrar a comparação final entre o antigo Chamados-PWA e o módulo Chamados integrado à Deja Platform.

## Classificações

Cada funcionalidade auditada deve ser classificada como um dos seguintes estados:

- Migrada;
- Melhorada; 
- Substituída;
- Descartada intencionalmente;
- Pendente.

## Ticket-card

Status: **auditado e concluído**.

Resultados:

- título — Migrado.
- cliente — Migrado.
- status — Migrado.
- prioridade — Migrada.
- prazo/SLA — Migrado e Melhorado.
- descrição — Migrada.
- responsável — Migrado e Melhorado.
- data de criação — Migrada.
- WhatsApp e cidade no card — Descartados intencionalmente; dados disponíveis no modal do cliente.
- detalhes — Migrado.
- cliente — Migrado com visualização rápida.
- editar — Migrado com controle de permissão.
- excluir — Descartado intencionalmente; histórico preservado por encerramento/reabertura.
- atualizado em — Melhoria da Deja Platform.
- encerrado em — Melhoria da Deja Platform.
- alteração de status no card — Melhoria da Deja Platform.

## Busca de chamados

Status: **auditado e concluído**.

PWA original:

- pesquisava no frontend;
- título;
- descrição;
- responsável;
- razão social;
- nome fantasia.

Deja Platform atual:

- a busca é realizada no backend;
- usa o parâmetro `search`;
- pesquisa por título, descrição, responsável, razão social e nome fantasia;
- mantém filtros independentes por cliente, status e prioridade.

Classificação: **Migrada e Melhorada.**

## Listagem de tickets

Status: **auditado e concluído**.

PWA original:

- botão para novo chamado;
- busca textual e seleção de status;
- busca e filtragem local no frontend;
- formulário de criação e edição integrado à página;
- ações de detalhes, cliente, edição e exclusão nos cards.

Deja Platform atual:

- abertura de novo chamado com controle por `canManage()`;
- busca realizada no backend;
- filtros independentes por cliente, status e prioridade;
- contador de resultados;
- estados de carregamento, vazio e erro;
- ação de nova tentativa em caso de erro;
- mensagens de sucesso e falha operacional;
- criação e edição integradas ao `ticket-management`;
- cliente imutável após a abertura do chamado;
- responsável selecionado entre usuários elegíveis;
- limites de 150 caracteres para título e 5000 para descrição;
- operações de gestão condicionadas a permissão;
- exclusão de ticket não oferecida; o histórico é preservado por encerramento e reabertura.

Classificação: **Migrada e Melhorada.**


## Fluxo de detalhes

Status: **auditado e concluído**.

PWA original:

- exibia título, status, prioridade e situação do prazo/SLA;
- apresentava descrição, responsável e datas do chamado;
- no modo administrativo, permitia edição do chamado;
- mostrava os dados completos do cliente em um bloco próprio;
- exibia histórico de atividades;
- integrava comentários;
- integrava anexos;
- suportava os modos administrativo e portal do cliente.

Deja Platform atual:

- exibe título, descrição, prioridade e status;
- permite edição inline de título e descrição para usuários com permissão;
- permite alteração controlada de status, prioridade e responsável;
- apresenta responsável, data de abertura, atualização e encerramento;
- apresenta vencimento do prazo, situação do prazo e tempo restante enquanto o chamado estiver aberto;
- para chamados encerrados, preserva o resultado histórico do prazo comparando `closedAt` com o vencimento;
- integra comentários públicos e internos com controle de visibilidade;
- integra anexos com visualização e exclusão condicionadas à permissão;
- mantém timeline operacional do chamado;
- usa limite de 150 caracteres para o título e 5000 para a descrição;
- os dados completos do cliente não são duplicados no detalhe; a consulta foi substituída pela visualização rápida do cliente disponível no fluxo de listagem.

Classificação: **Migrada e Melhorada.**


## Comentários

Status: **auditado e concluído**.

PWA original:

- apresentava comentários no detalhe do chamado;
- no modo administrativo, exibia todos os comentários;
- no modo cliente, filtrava somente comentários públicos;
- permitia inclusão de comentário quando autorizada pelo fluxo;
- o componente não permitia selecionar explicitamente a visibilidade.

Deja Platform atual:

- mantém comentários públicos e internos no fluxo administrativo;
- permite seleção explícita da visibilidade ao adicionar comentário pela equipe;
- limita o conteúdo a 5000 caracteres;
- apresenta autor, data e identificação visual da visibilidade;
- possui estados de envio e tratamento de erro;
- o portal do cliente lista somente comentários públicos;
- comentários criados pelo cliente são forçados como públicos pelo backend;
- o backend valida que o chamado pertence ao cliente autenticado antes de listar ou criar comentários;
- comentários internos nunca são expostos pelo endpoint do portal.

Classificação: **Migrada e Melhorada.**

## Anexos

Status: **auditado e concluído**.

PWA original:

- permitia anexar PNG, JPEG, WEBP e PDF;
- condicionava inclusão e exclusão às permissões;
- permitia visualizar o arquivo em nova aba;
- distinguia visualmente imagens de PDFs;
- exibia nome original, tamanho e data;
- rejeitava no frontend arquivos com tipos não permitidos.

Deja Platform atual:

- mantém os mesmos tipos permitidos: PNG, JPEG, WEBP e PDF;
- aplica a restrição de tipos também no backend;
- possui limite máximo de tamanho configurável;
- valida papéis e escopo organizacional para leitura, inclusão, download e exclusão;
- registra autor, data, nome original, tipo e tamanho do arquivo;
- bloqueia operações concorrentes durante envio ou exclusão;
- apresenta mensagens de erro na interface;
- realiza download autenticado e abre o arquivo em nova aba;
- remove o registro e o arquivo físico na exclusão;
- registra eventos de inclusão e remoção na timeline;
- o portal do cliente permite listar, visualizar e baixar somente anexos pertencentes aos seus próprios chamados.

Classificação: **Migrada e Melhorada.**

## Timeline / histórico

Status: **auditado e concluído**.

PWA original:

- registrava criação do chamado;
- mudança de status;
- mudança de prioridade;
- mudança de responsável;
- comentários;
- anexos adicionados;
- anexos removidos;
- apresentava autor, data e descrição do evento;
- convertia valores técnicos de status e prioridade em rótulos legíveis.

Deja Platform atual:

- registra criação do chamado;
- registra mudança de status;
- registra mudança de prioridade;
- registra mudança de responsável;
- registra alterações gerais do chamado por meio do evento updated;
- registra comentários como comment_added;
- registra inclusão de anexos como attachment_added;
- registra remoção de anexos como attachment_removed;
- apresenta datas e descrições legíveis;
- converte status e prioridade para rótulos de apresentação;
- na troca de responsável, utiliza valores de apresentação com nome do usuário quando disponíveis;
- comentários administrativos e comentários do portal passam a gerar evento de timeline;
- o portal recebe uma representação segura do histórico, sem expor identificadores internos de usuário.

Classificação: **Migrada e Melhorada.**

## Portal do Cliente

Status: **auditado e concluído**.

PWA original:

- acesso protegido por autenticação e papel client;
- listava somente os chamados vinculados ao cliente autenticado;
- permitia abrir novo chamado com assunto e descrição;
- apresentava status, prioridade, descrição e data de abertura;
- permitia abrir a tela de detalhes do chamado;
- reutilizava a tela de detalhes do módulo de tickets para acompanhamento.

Deja Platform atual:

- mantém acesso restrito ao usuário externo vinculado a um Cliente;
- deriva organização, tenant, ambiente e cliente a partir do vínculo autenticado, sem aceitar esses identificadores do frontend;
- lista somente chamados pertencentes ao Cliente autenticado;
- possui tratamento explícito de carregamento, erro e nova tentativa;
- permite abrir novos chamados com validação de título até 150 caracteres e descrição até 5000 caracteres;
- evita envio duplicado durante a criação;
- atualiza a lista imediatamente após a abertura do chamado;
- exibe status, prioridade, responsável, data de abertura, última atualização e fechamento;
- possui tela própria de detalhes do Portal;
- permite adicionar e consultar comentários públicos;
- impede leitura de comentários internos;
- registra comentários públicos na timeline;
- filtra eventos de comentários internos da timeline do Portal, evitando exposição indireta de atividade interna;
- permite consultar e visualizar anexos vinculados ao chamado;
- apresenta histórico seguro com alterações de status, prioridade, responsável, comentários públicos e eventos de anexos;
- converte identificadores internos de responsáveis em nomes antes de devolver a timeline ao Portal;
- não expõe identificadores internos de usuário nas respostas públicas;
- possui domínio, serviço e repositório HTTP próprios no frontend;
- teve o contrato PortalTimelineEventType alinhado aos eventos efetivamente retornados pela API;
- possui fluxo explícito de logout.

Classificação: **Migrada e Melhorada.**

## Fila de atendimento

Status: **auditado e concluído**.

PWA original:

- utilizava quadro Kanban com quatro colunas: aberto, em atendimento, pendente e fechado;
- permitia mover chamados entre colunas por drag-and-drop;
- não executava ação ao mover dentro da mesma coluna;
- exibia contador por coluna e estado vazio;
- os cards apresentavam título, status, prioridade, cliente, descrição, responsável e última atualização;
- os chamados eram ordenados pela atualização mais recente;
- a mudança de coluna delegava a atualização do status ao serviço de tickets.

Deja Platform atual:

- mantém o quadro Kanban com quatro estados do chamado;
- mantém drag-and-drop entre colunas para alteração de status;
- ignora movimentação dentro da mesma coluna;
- permite uso da fila em modo somente leitura;
- bloqueia movimentação para usuários sem permissão de gestão;
- bloqueia temporariamente apenas o chamado que está sendo atualizado;
- possui carregamento assíncrono explícito, atualização manual e tentativa novamente em caso de falha;
- utiliza atualização otimista da interface com rollback automático quando a API rejeita a mudança;
- apresenta mensagens específicas para sucesso, encerramento, reabertura e falhas de autorização, conflito, não encontrado e validação;
- mantém contador por coluna e estado vazio;
- mantém nos cards prioridade, status, título, cliente, descrição, responsável e última atualização;
- resolve nomes de clientes a partir dos dados já carregados;
- chamados ativos são ordenados por prioridade, da crítica para a baixa;
- em empate de prioridade, chamados ativos mais antigos são apresentados primeiro;
- chamados fechados permanecem ordenados pela atualização mais recente;
- possui testes específicos para permissão, persistência, rollback, prioridade, antiguidade, chamados fechados e filtragem por status.

Classificação: **Migrada e Melhorada.**

## Dashboard

Status: **auditado e concluído**.

PWA original:

- apresentava resumo operacional de clientes e chamados;
- exibia totais por status e prioridade;
- calculava chamados dentro do prazo, próximos do vencimento e vencidos;
- calculava percentual de atendimentos dentro e fora do SLA;
- apresentava SLA por prioridade;
- apresentava SLA por responsável;
- apresentava evolução mensal de chamados abertos, encerrados e cumprimento de SLA;
- calculava tempo médio de atendimento;
- calculava MTTR;
- calculava taxa de resolução;
- calculava taxa de reabertura;
- apresentava backlog total;
- apresentava MTTR por responsável;
- apresentava reabertura por responsável;
- apresentava backlog por responsável;
- apresentava backlog por prioridade;
- apresentava ranking consolidado de responsáveis;
- apresentava clientes com mais chamados;
- apresentava chamados abertos há mais tempo;
- apresentava chamados recentes;
- concentrava boa parte dos cálculos em um serviço Angular dependente dos serviços globais de clientes, chamados e atividades.

Deja Platform atual:

- mantém o resumo operacional de clientes e chamados;
- mantém indicadores por status e prioridade;
- mantém indicadores de chamados dentro do prazo, próximos do vencimento e vencidos;
- mantém percentuais de atendimento dentro e fora do SLA;
- mantém SLA por prioridade e por responsável;
- mantém evolução mensal de abertura, encerramento e cumprimento de SLA;
- mantém tempo médio de atendimento, MTTR, taxa de resolução, taxa de reabertura e backlog;
- mantém indicadores de MTTR, reabertura e backlog por responsável;
- mantém backlog por prioridade;
- mantém ranking consolidado de responsáveis;
- mantém principais clientes, chamados mais antigos e chamados recentes;
- utiliza a timeline consolidada para cálculo de MTTR e identificação de reaberturas;
- recebe clientes, chamados e timeline por meio de uma fonte de dados explícita, reduzindo acoplamento com estado global;
- separa a construção dos indicadores em buildDashboardData, buildSlaData e buildManagerData;
- mantém regras de SLA centralizadas e reutilizáveis;
- possui testes específicos para resumo operacional, SLA, MTTR baseado em timeline, reabertura e backlog por responsável;
- preserva as principais regras de cálculo existentes no PWA original sem perda funcional identificada na auditoria.

Classificação: **Migrada e Melhorada.**

## Autorização

Status: **auditado e concluído**.

PWA original:

- restringia o Portal a usuários com papel `client`;
- utilizava autenticação e papel do usuário para separar Portal e área interna;
- possuía controle funcional mais simples e menos granular entre leitura e operação.

Deja Platform atual:

- separa explicitamente usuários internos e usuários `client`;
- `client` acessa somente o Portal;
- usuários internos são redirecionados para fora do Portal;
- usuários `client` são redirecionados para o Portal ao tentar acessar o Workspace;
- o acesso ao Workspace também respeita os módulos habilitados por meio de `moduleGuard`;
- `platform_admin` possui acesso global aos módulos;
- demais usuários internos precisam ter o módulo `chamados` habilitado;
- tickets podem ser consultados por `platform_admin`, `organization_admin`, `tenant_admin`, `manager`, `analyst` e `viewer`;
- tickets podem ser operados por todos os papéis anteriores, exceto `viewer`;
- responsáveis elegíveis são `organization_admin`, `tenant_admin`, `manager` e `analyst`;
- clientes podem ser consultados por todos os papéis internos;
- clientes podem ser gerenciados por `platform_admin`, `organization_admin`, `tenant_admin` e `manager`;
- vínculos entre usuários externos e clientes ficam restritos a `platform_admin`, `organization_admin` e `tenant_admin`;
- comentários, anexos, timeline e responsáveis reutilizam a mesma matriz de autorização dos tickets;
- o frontend replica a matriz do backend por meio de `canManage`, reduzindo ações incompatíveis com a API;
- o Portal deriva e valida o Cliente vinculado ao usuário autenticado;
- o Portal não permite acesso a chamados de outro Cliente;
- comentários internos não são expostos ao Portal, nem diretamente nem por eventos de timeline;
- as principais regras de autorização e escopo possuem cobertura automatizada.

Validação:

- 80 testes de autorização e isolamento executados com sucesso;
- cobertura inclui Clientes, Tickets, responsáveis, vínculos de usuários externos e Portal.

Classificação: **Migrada e Melhorada.**
## Próximos itens

