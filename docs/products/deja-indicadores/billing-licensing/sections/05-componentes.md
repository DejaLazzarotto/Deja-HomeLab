# 05. Componentes

## Visão Geral

O Billing / Licensing é composto por um conjunto de serviços institucionais especializados que, em conjunto, implementam todo o ciclo de vida comercial da Deja Platform.

Cada componente possui responsabilidades bem definidas e comunica-se por contratos institucionais, preservando baixo acoplamento e alta escalabilidade.

---

## Visão dos Componentes

```
Billing / Licensing
│
├── Commercial Catalog Service
├── Plan Service
├── Subscription Service
├── Contract Service
├── License Service
├── Eligibility Service
├── Consumption Meter
├── Usage Aggregator
├── Billing Service
├── Commercial Policy Engine
├── Pricing Engine
├── Invoice Generator
├── Commercial Event Publisher
├── Audit Service
└── Reporting Service
```

---

## Commercial Catalog Service

Responsável pelo catálogo institucional de ofertas comerciais.

Gerencia:

- produtos;
- módulos;
- capacidades comercializáveis;
- add-ons;
- recursos opcionais;
- versões comerciais.

Não realiza controle de licenciamento nem faturamento.

---

## Plan Service

Gerencia os planos disponíveis.

Suas responsabilidades incluem:

- cadastro de planos;
- versionamento;
- vigência;
- recursos disponíveis;
- limites;
- regras comerciais.

Os planos constituem modelos reutilizáveis para assinaturas.

---

## Subscription Service

Gerencia todo o ciclo de vida das assinaturas.

Inclui:

- contratação;
- ativação;
- renovação;
- suspensão;
- cancelamento;
- encerramento.

Cada assinatura está vinculada a um contrato e a um Tenant.

---

## Contract Service

Representa os contratos comerciais.

Controla:

- vigência;
- termos comerciais;
- condições especiais;
- reajustes;
- vínculos com organizações;
- histórico contratual.

---

## License Service

Responsável pela emissão e manutenção das licenças.

Executa:

- criação;
- renovação;
- revogação;
- expiração;
- atualização;
- consulta.

As licenças representam a autorização oficial de uso da plataforma.

---

## Eligibility Service

Realiza todas as validações comerciais antes da execução de funcionalidades.

Verifica, entre outros fatores:

- licença válida;
- assinatura ativa;
- plano contratado;
- limites de consumo;
- políticas aplicáveis;
- período de vigência;
- ambiente autorizado.

É o principal ponto de integração dos demais componentes da plataforma com o Billing / Licensing.

---

## Consumption Meter

Captura continuamente eventos de utilização da plataforma.

Pode registrar:

- execuções;
- usuários ativos;
- armazenamento utilizado;
- processamento consumido;
- chamadas de API;
- utilização de módulos;
- consumo de capacidades.

---

## Usage Aggregator

Consolida os eventos de consumo.

Suporta:

- agrupamentos;
- fechamento de períodos;
- cálculo de métricas comerciais;
- consolidação por Tenant;
- consolidação por Organização;
- consolidação por contrato.

---

## Billing Service

Responsável pela consolidação dos valores comerciais.

Executa:

- cálculo de cobranças;
- aplicação de franquias;
- créditos;
- débitos;
- descontos;
- períodos de faturamento.

Não executa pagamento nem integração bancária.

---

## Commercial Policy Engine

Centraliza todas as políticas comerciais reutilizáveis.

Exemplos:

- limites;
- períodos promocionais;
- upgrades;
- downgrades;
- regras de renovação;
- elegibilidade.

---

## Pricing Engine

Calcula os valores aplicáveis a produtos, planos e consumo.

Pode considerar:

- preço fixo;
- preço variável;
- consumo;
- descontos;
- contratos especiais;
- campanhas comerciais.

---

## Invoice Generator

Produz os documentos comerciais utilizados pelo processo de faturamento.

Pode gerar:

- demonstrativos;
- pré-faturas;
- memória de cálculo;
- resumos de consumo.

A emissão fiscal permanece responsabilidade de sistemas externos.

---

## Commercial Event Publisher

Publica eventos institucionais relacionados às operações comerciais.

Exemplos:

- plano criado;
- assinatura ativada;
- licença emitida;
- consumo registrado;
- faturamento encerrado;
- contrato alterado.

Esses eventos alimentam Observability, Audit e demais componentes interessados.

---

## Audit Service

Mantém histórico permanente das operações comerciais.

Registra:

- alterações;
- aprovações;
- renovações;
- cancelamentos;
- validações;
- consumo;
- faturamentos.

Toda informação permanece rastreável durante o ciclo de vida da plataforma.

---

## Reporting Service

Disponibiliza informações consolidadas para consultas gerenciais e operacionais.

Pode fornecer indicadores como:

- receita recorrente;
- consumo por Tenant;
- utilização de planos;
- crescimento de assinaturas;
- distribuição de licenças;
- evolução comercial.

---

## Arquitetura Modular

Todos os componentes são independentes, reutilizáveis e desacoplados.

A comunicação ocorre por contratos institucionais e eventos publicados, permitindo evolução contínua da arquitetura sem impacto sobre consumidores ou módulos da plataforma.