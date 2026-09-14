# Funcionalidades e regras de negócio — Deja Chamados

## Clientes

Mantém o cadastro dos clientes atendidos pelo módulo Chamados, com dados cadastrais, contato e vínculo com o escopo organizacional.

## Chamados

Cada chamado possui título, descrição, cliente, status, prioridade, responsável, autoria, datas e histórico.

## Status

- Aberto (`open`)
- Em Atendimento (`in_progress`)
- Pendente (`pending`)
- Encerrado (`closed`)

As transições são controladas pela aplicação.

## Prioridade

- Baixa (`low`)
- Média (`medium`)
- Alta (`high`)
- Crítica (`critical`)

## Prazo / SLA

Prazo atual por prioridade:

- Baixa: 72 horas
- Média: 48 horas
- Alta: 24 horas
- Crítica: 4 horas

Para chamados encerrados, o resultado é calculado comparando `closedAt` com o vencimento, preservando o estado histórico do prazo.

## Busca

A listagem de chamados permite busca por:

- título; 
- descrição;
- responsável;
- razão social do cliente;
- nome fantasia do cliente.

A busca utiliza o parâmetro `search` da API de chamados.


## Listagem e filtros

A listagem de chamados oferece:

- busca textual processada pela API;
- filtro por cliente;
- filtro por status;
- filtro por prioridade;
- contador de resultados;
- estados de carregamento, vazio e erro;
- nova tentativa em caso de falha;
- criação e edição integradas ao fluxo de gerenciamento;
- seleção de responsável entre usuários elegíveis;
- operações administrativas condicionadas às permissões do usuário.

O cliente do chamado permanece imutável após a abertura, preservando a integridade do histórico.

## Detalhes do chamado

A tela de detalhes apresenta:

- título e descrição;
- prioridade e status;
- responsável;
- datas de abertura, atualização e encerramento;
- vencimento do prazo;
- situação do prazo;
- tempo restante para chamados ainda não encerrados;
- comentários públicos e internos;
- anexos;
- timeline de eventos.

Usuários com permissão de gerenciamento podem editar título e descrição, alterar status, prioridade e responsável, adicionar comentários internos ou públicos e operar anexos.

O título possui limite de 150 caracteres e a descrição, 5000 caracteres.

Os dados cadastrais completos do cliente não são duplicados na tela de detalhes; sua consulta é realizada pela visualização rápida de cliente disponível no fluxo de chamados.

## Encerramento

Tickets não são excluídos no fluxo atual. O histórico é preservado por meio de encerramento e reabertura conforme as regras de transição.

## Observação
Novas regras serão adicionadas à medida que a auditoria final avançar.
