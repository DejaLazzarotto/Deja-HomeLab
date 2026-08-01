# 07. Consumo e Medição

## Visão Geral

O Billing / Licensing estabelece um modelo institucional de medição de consumo que permite registrar, consolidar e contabilizar a utilização dos recursos da Deja Platform.

O consumo constitui um ativo arquitetural e pode ser utilizado tanto para controle operacional quanto para aplicação de regras comerciais, faturamento e geração de indicadores.

---

## Objetivos

O modelo de consumo possui os seguintes objetivos:

- medir a utilização da plataforma;
- suportar modelos baseados em consumo;
- controlar limites contratuais;
- subsidiar o faturamento;
- produzir informações gerenciais;
- fornecer rastreabilidade completa das utilizações.

---

## Modelo Conceitual

```
Evento de Uso
        │
        ▼
Consumption Meter
        │
        ▼
Usage Record
        │
        ▼
Usage Aggregator
        │
        ▼
Consumption Summary
        │
        ▼
Billing
```

Cada etapa adiciona informações sem modificar os registros originais, preservando a rastreabilidade.

---

## Eventos de Consumo

Todo recurso comercialmente relevante pode produzir eventos de consumo.

Exemplos:

- execução de indicadores;
- chamadas de API;
- processamento de workflows;
- utilização de módulos;
- armazenamento consumido;
- usuários ativos;
- criação de ambientes;
- execução de automações;
- processamento de IA;
- utilização de integrações.

Novos tipos de eventos poderão ser incorporados sem alterações estruturais.

---

## Usage Record

Cada evento gera um **Usage Record**, contendo informações como:

- identificador do evento;
- Tenant;
- Organização;
- Ambiente;
- recurso consumido;
- quantidade;
- unidade de medida;
- data e hora;
- origem da operação;
- contexto de execução.

Os registros são imutáveis.

---

## Unidades de Medição

A arquitetura não impõe uma unidade única de consumo.

Entre as unidades suportadas estão:

- quantidade;
- tempo;
- armazenamento;
- processamento;
- requisições;
- usuários;
- execuções;
- créditos;
- eventos;
- capacidade computacional.

Novas unidades poderão ser adicionadas conforme a evolução da plataforma.

---

## Consolidação

O Usage Aggregator consolida os registros individuais em períodos configuráveis.

A consolidação pode ocorrer por:

- Tenant;
- Organização;
- Produto;
- Plano;
- Assinatura;
- Contrato;
- Ambiente;
- capacidade;
- período de faturamento.

---

## Limites Operacionais

Os registros de consumo permitem validar limites definidos pelo plano ou pela licença.

Exemplos:

- máximo de usuários;
- máximo de execuções;
- limite de armazenamento;
- chamadas de API;
- processamento mensal;
- utilização de IA;
- consumo de créditos.

A validação é realizada pelo Eligibility Service.

---

## Modelos de Cobrança

O consumo pode ser utilizado em diferentes estratégias comerciais, como:

- assinatura fixa;
- pay-per-use;
- franquia com excedente;
- créditos pré-pagos;
- cobrança por capacidade;
- cobrança híbrida;
- cobrança por eventos.

A arquitetura permanece independente da política comercial adotada.

---

## Rastreabilidade

Todos os eventos de consumo permanecem registrados para fins de:

- auditoria;
- conferência de faturamento;
- análises gerenciais;
- investigação de incidentes;
- reconciliação comercial.

Nenhum processo de consolidação elimina os registros originais.

---

## Integração com Billing

Os resumos consolidados de consumo são disponibilizados ao Billing Service, que aplica:

- regras de precificação;
- franquias;
- descontos;
- créditos;
- políticas comerciais;
- cálculo dos valores faturáveis.

---

## Resultado Esperado

Ao final do processo de medição, a Deja Platform dispõe de um histórico íntegro, auditável e consolidado da utilização de seus recursos, permitindo suportar diferentes modelos de monetização e faturamento com elevada precisão e escalabilidade.