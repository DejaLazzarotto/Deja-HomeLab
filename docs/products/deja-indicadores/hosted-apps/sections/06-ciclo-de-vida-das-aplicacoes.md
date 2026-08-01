# 06. Ciclo de Vida das Aplicações

## Visão Geral

A Hosted Apps é responsável por administrar todo o ciclo de vida das aplicações hospedadas na Deja Platform.

O ciclo de vida define as etapas pelas quais uma aplicação transita desde seu registro institucional até sua descontinuação, garantindo rastreabilidade, segurança, governança e padronização operacional.

Todas as mudanças de estado são controladas pelo Lifecycle Manager e registradas para auditoria.

---

## Etapas do Ciclo de Vida

O ciclo de vida institucional compreende as seguintes etapas:

1. Registro
2. Validação
3. Publicação
4. Implantação
5. Configuração
6. Inicialização
7. Operação
8. Atualização
9. Suspensão
10. Reativação
11. Remoção
12. Descontinuação

Cada etapa possui regras próprias de transição e validação.

---

## Registro

O registro representa a entrada oficial da aplicação na plataforma.

Nesta etapa são definidos:

- identificador único
- metadados
- proprietário
- categoria
- manifesto
- versões iniciais
- dependências
- políticas institucionais

Após o registro, a aplicação torna-se conhecida pela Hosted Apps, porém ainda não está disponível para execução.

---

## Validação

Antes da publicação, a aplicação passa por validações institucionais, incluindo:

- integridade do manifesto
- consistência dos metadados
- compatibilidade de versões
- dependências obrigatórias
- conformidade arquitetural
- requisitos de segurança

Somente aplicações aprovadas podem prosseguir para implantação.

---

## Publicação

A publicação torna a aplicação disponível para implantação nos ambientes autorizados.

Nesta fase são definidos:

- versões publicadas
- ambientes permitidos
- políticas de distribuição
- estratégias de atualização

A publicação não implica execução imediata.

---

## Implantação

A implantação disponibiliza a aplicação em um ambiente específico.

Durante esta etapa são realizados:

- provisionamento de recursos
- instalação dos artefatos
- aplicação das configurações
- validações pós-deployment

A implantação pode ocorrer de forma independente para cada ambiente.

---

## Configuração

Após a implantação, a aplicação recebe suas configurações institucionais.

Essas configurações são obtidas exclusivamente por meio da capacidade Configuration, respeitando:

- organização
- tenant
- ambiente
- contexto de execução

---

## Inicialização

A inicialização coloca a aplicação em operação.

O Runtime Manager é responsável por:

- iniciar instâncias
- validar disponibilidade
- registrar eventos operacionais
- comunicar o estado da aplicação

---

## Operação

Durante a operação, a Hosted Apps acompanha continuamente:

- disponibilidade
- consumo de recursos
- estado operacional
- eventos
- métricas
- logs
- traces

Essas informações são encaminhadas para a capacidade Observability.

---

## Atualização

Atualizações são executadas de forma controlada.

O processo contempla:

- validação da nova versão
- implantação
- migração de configurações quando aplicável
- monitoramento pós-atualização
- possibilidade de rollback

---

## Suspensão e Reativação

Aplicações podem ser suspensas temporariamente por motivos administrativos, operacionais ou de segurança.

Posteriormente, podem ser reativadas preservando sua configuração e histórico operacional.

---

## Remoção e Descontinuação

Quando uma aplicação deixa de ser utilizada, inicia-se seu processo de remoção.

A descontinuação envolve:

- encerramento da execução
- remoção dos artefatos implantados
- revogação de acessos
- preservação dos registros históricos
- auditoria final

A rastreabilidade permanece disponível mesmo após a remoção da aplicação.

---

## Garantias Arquiteturais

O ciclo de vida foi projetado para assegurar:

- operações previsíveis
- transições controladas
- rastreabilidade completa
- compatibilidade entre versões
- segurança operacional
- integração institucional
- alta disponibilidade
- evolução contínua da infraestrutura de hospedagem