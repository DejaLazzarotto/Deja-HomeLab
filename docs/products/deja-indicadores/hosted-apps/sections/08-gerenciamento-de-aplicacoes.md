# 08. Gerenciamento de Aplicações

## Visão Geral

A Hosted Apps estabelece o modelo institucional de gerenciamento das aplicações hospedadas na Deja Platform.

Esse gerenciamento compreende todas as operações administrativas necessárias para controlar aplicações durante seu ciclo de vida, garantindo padronização operacional, rastreabilidade, governança e integração com as demais capacidades institucionais.

Todas as operações são executadas exclusivamente por contratos públicos da Hosted Apps.

---

## Objetivos

O gerenciamento de aplicações possui os seguintes objetivos:

- centralizar operações administrativas
- controlar versões implantadas
- administrar estados operacionais
- garantir disponibilidade
- preservar rastreabilidade
- suportar múltiplos ambientes
- integrar-se às capacidades institucionais

---

## Cadastro Administrativo

Cada aplicação possui um registro administrativo contendo:

- identificador institucional
- nome
- categoria
- proprietário
- organização responsável
- tenant associado
- ambientes disponíveis
- versões implantadas
- estado operacional
- histórico administrativo

Esse cadastro representa a referência oficial para todas as operações de gerenciamento.

---

## Operações Administrativas

Entre as operações suportadas estão:

- registrar aplicação
- publicar versão
- implantar aplicação
- iniciar execução
- interromper execução
- reiniciar aplicação
- suspender operação
- reativar aplicação
- atualizar versão
- realizar rollback
- remover aplicação
- descontinuar aplicação

Todas as operações são registradas para auditoria.

---

## Gerenciamento de Versões

A Hosted Apps mantém controle institucional das versões hospedadas.

São administradas informações como:

- versão ativa
- versões disponíveis
- histórico de atualizações
- compatibilidade
- rollback permitido
- status de homologação

Cada ambiente pode possuir versões distintas conforme as políticas de deployment.

---

## Gerenciamento de Ambientes

As aplicações podem ser administradas independentemente em cada ambiente.

Entre os ambientes suportados:

- desenvolvimento
- homologação
- produção
- ambientes privados
- ambientes dedicados

Cada ambiente possui políticas próprias de configuração, segurança e operação.

---

## Disponibilidade Operacional

O gerenciamento acompanha continuamente:

- estado das aplicações
- disponibilidade
- saúde operacional
- instâncias ativas
- consumo de recursos
- eventos relevantes

Essas informações subsidiam decisões administrativas e operacionais.

---

## Administração Centralizada

Toda administração é realizada pelas capacidades institucionais:

- Administration Platform
- Administration Console

A Hosted Apps fornece apenas os contratos públicos necessários para execução dessas operações.

---

## Integração Institucional

O gerenciamento de aplicações integra-se com:

- Tenant Management
- Security
- Configuration
- Observability
- API Gateway
- API Management
- Marketplace

Essa integração garante consistência operacional em toda a plataforma.

---

## Auditoria e Rastreabilidade

Todas as operações administrativas geram registros contendo:

- operação executada
- aplicação afetada
- versão
- ambiente
- organização
- tenant
- usuário responsável
- data e hora
- resultado da operação

Esses registros permanecem disponíveis para auditoria institucional.

---

## Garantias Arquiteturais

O modelo de gerenciamento assegura:

- administração padronizada
- operações consistentes
- controle centralizado
- rastreabilidade completa
- segurança operacional
- escalabilidade
- compatibilidade evolutiva
- integração plena com a arquitetura institucional da Deja Platform