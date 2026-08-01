# 12. Integração com Observability

## Objetivo

A Workspace Applications integra-se à capacidade institucional Observability para garantir monitoramento contínuo, rastreabilidade operacional, coleta de métricas e diagnóstico das aplicações executadas no Workspace da Deja Platform.

A Observability permanece como autoridade institucional sobre telemetria, logs, métricas, eventos e tracing, enquanto a Workspace Applications atua exclusivamente como produtora de informações operacionais.

---

## Princípios

A integração observa os seguintes princípios:

- Observability é a autoridade institucional sobre monitoramento;
- telemetria é centralizada;
- logs são padronizados;
- métricas seguem contratos institucionais;
- tracing distribuído é suportado;
- correlação de eventos é obrigatória;
- aplicações não implementam infraestrutura própria de observabilidade.

---

## Informações produzidas

Durante o ciclo de vida das aplicações são produzidas informações como:

- registro de aplicações;
- carregamento;
- inicialização;
- ativação;
- suspensão;
- retomada;
- encerramento;
- descarregamento;
- falhas operacionais;
- tempo de carregamento;
- tempo de inicialização;
- estado operacional.

Esses dados são encaminhados à Observability por contratos públicos.

---

## Logs institucionais

A Workspace Applications produz logs relacionados às operações administrativas e ao ciclo de vida das aplicações.

Entre eles:

- operações administrativas;
- alterações de estado;
- validações;
- carregamentos;
- falhas de integração;
- erros de inicialização;
- incompatibilidades detectadas.

A estrutura dos logs é definida exclusivamente pela Observability.

---

## Métricas

São disponibilizadas métricas operacionais, incluindo:

- número de aplicações registradas;
- aplicações carregadas;
- aplicações ativas;
- aplicações suspensas;
- falhas de carregamento;
- tempo médio de inicialização;
- tempo médio de ativação;
- quantidade de reinicializações;
- disponibilidade operacional.

Essas métricas apoiam a operação e a capacidade de planejamento da plataforma.

---

## Tracing distribuído

As operações executadas pela Workspace Applications podem participar de traces distribuídos da plataforma.

Exemplos:

- instalação de aplicações;
- carregamento;
- integração com o Workspace Runtime;
- inicialização;
- atualizações;
- encerramentos.

A correlação entre capacidades facilita o diagnóstico de falhas complexas.

---

## Integração operacional

A integração com a Observability permite:

- acompanhamento em tempo real;
- diagnóstico operacional;
- auditoria técnica;
- identificação de gargalos;
- análise de desempenho;
- suporte à operação;
- geração de indicadores institucionais.

Todo o fluxo ocorre exclusivamente por contratos públicos.

---

## Benefícios

A integração proporciona:

- monitoramento centralizado;
- rastreabilidade completa;
- padronização dos registros;
- diagnóstico facilitado;
- redução do tempo de resposta a incidentes;
- apoio à governança operacional;
- escalabilidade do monitoramento;
- evolução independente entre Workspace Applications e Observability.

Dessa forma, a Workspace Applications contribui para uma operação transparente, previsível e observável em toda a Deja Platform.