# 11. Integração com Security

## Visão Geral

A Hosted Apps integra-se à capacidade institucional Security para garantir que todas as aplicações hospedadas operem de acordo com as políticas oficiais de identidade, autenticação, autorização, proteção de dados e auditoria da Deja Platform.

A Security permanece como a única autoridade responsável pelas decisões relacionadas à segurança da plataforma.

A Hosted Apps apenas consome seus contratos públicos, não implementando mecanismos próprios de autenticação ou autorização.

---

## Objetivos da Integração

A integração possui os seguintes objetivos:

- autenticar identidades
- autorizar operações
- aplicar políticas de acesso
- proteger credenciais
- gerenciar segredos
- registrar auditorias
- preservar o isolamento de segurança

---

## Autenticação

Toda identidade utilizada pelas aplicações hospedadas é autenticada por meio da capacidade Security.

Entre as identidades suportadas estão:

- usuários
- administradores
- serviços
- aplicações
- integrações sistêmicas

Nenhuma autenticação é realizada diretamente pela Hosted Apps.

---

## Autorização

Antes da execução de qualquer operação administrativa ou operacional, a Hosted Apps consulta a Security para validar as permissões necessárias.

As políticas podem considerar:

- organização
- tenant
- ambiente
- função
- perfil
- contexto da operação

---

## Credenciais e Segredos

Credenciais utilizadas pelas aplicações hospedadas são administradas exclusivamente pela Security.

Isso inclui:

- chaves de acesso
- certificados
- tokens
- senhas
- segredos de integração

A Hosted Apps nunca armazena ou gerencia credenciais diretamente.

---

## Políticas de Segurança

Durante a execução das aplicações, são aplicadas automaticamente políticas relacionadas a:

- controle de acesso
- segregação de funções
- isolamento entre tenants
- proteção de recursos
- conformidade institucional

Essas políticas são definidas e mantidas pela Security.

---

## Auditoria

Toda operação relevante realizada pela Hosted Apps gera eventos de auditoria encaminhados à Security.

São registrados, entre outros:

- autenticações
- autorizações
- implantações
- atualizações
- reinicializações
- remoções
- alterações administrativas

---

## Comunicação Segura

Toda integração entre Hosted Apps e Security ocorre por contratos públicos seguros.

Essa comunicação garante:

- integridade
- confidencialidade
- autenticação mútua
- rastreabilidade

Não existe acesso direto às estruturas internas da Security.

---

## Benefícios Arquiteturais

A integração com Security proporciona:

- segurança institucional centralizada
- autenticação padronizada
- autorização consistente
- proteção de credenciais
- auditoria completa
- isolamento seguro
- conformidade arquitetural
- evolução independente das capacidades