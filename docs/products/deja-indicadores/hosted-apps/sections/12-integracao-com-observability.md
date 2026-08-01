# 12. Integração com Observability

## Visão Geral

A Hosted Apps integra-se à capacidade institucional Observability para disponibilizar monitoramento contínuo, telemetria, rastreabilidade operacional e diagnóstico das aplicações hospedadas na Deja Platform.

A Observability permanece como a única capacidade responsável pela coleta, armazenamento, processamento e disponibilização das informações operacionais da plataforma.

A Hosted Apps produz eventos e telemetria, consumindo exclusivamente os contratos públicos disponibilizados pela Observability.

---

## Objetivos da Integração

A integração possui os seguintes objetivos:

- monitorar aplicações hospedadas
- acompanhar disponibilidade
- registrar eventos operacionais
- coletar métricas
- produzir logs estruturados
- disponibilizar traces distribuídos
- apoiar diagnóstico operacional

---

## Logs

Toda aplicação hospedada gera logs estruturados durante sua execução.

Entre os principais eventos registrados estão:

- inicialização
- encerramento
- implantação
- atualização
- rollback
- falhas
- alterações administrativas
- eventos operacionais

Os logs são encaminhados integralmente para a Observability.

---

## Métricas

A Hosted Apps disponibiliza métricas operacionais relacionadas a:

- aplicações implantadas
- aplicações ativas
- disponibilidade
- tempo de inicialização
- tempo de resposta
- consumo de recursos
- falhas de execução
- operações administrativas

Essas métricas subsidiam monitoramento e planejamento operacional.

---

## Tracing

As operações executadas pela Hosted Apps podem gerar traces distribuídos que permitem acompanhar o fluxo completo de execução entre as capacidades institucionais.

Os traces incluem informações como:

- contexto da operação
- aplicação
- organização
- tenant
- ambiente
- duração
- resultado

---

## Eventos Operacionais

Durante todo o ciclo de vida das aplicações são produzidos eventos operacionais, incluindo:

- registro
- publicação
- deployment
- inicialização
- interrupção
- atualização
- rollback
- remoção
- mudanças de estado

Esses eventos alimentam os mecanismos institucionais de observabilidade.

---

## Monitoramento

A integração permite acompanhamento contínuo de:

- disponibilidade das aplicações
- estado operacional
- utilização de recursos
- saúde das instâncias
- comportamento do deployment
- execução do runtime

Essas informações permanecem disponíveis para as capacidades administrativas.

---

## Dashboards Administrativos

As informações fornecidas pela Observability podem ser utilizadas pela:

- Administration Platform
- Administration Console

para construção de dashboards operacionais, indicadores de disponibilidade e acompanhamento em tempo real das aplicações hospedadas.

---

## Comunicação Institucional

Toda comunicação entre Hosted Apps e Observability ocorre exclusivamente por contratos públicos.

Não existe acesso direto aos mecanismos internos de coleta, armazenamento ou processamento da Observability.

Essa abordagem preserva baixo acoplamento e evolução independente das capacidades.

---

## Benefícios Arquiteturais

A integração com Observability assegura:

- monitoramento contínuo
- diagnóstico operacional
- rastreabilidade completa
- métricas institucionais
- alta visibilidade operacional
- suporte à auditoria
- apoio à governança
- evolução compatível com a arquitetura da Deja Platform