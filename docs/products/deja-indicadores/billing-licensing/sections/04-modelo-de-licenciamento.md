# 04. Modelo de Licenciamento

## Visão Geral

O modelo de licenciamento estabelece como os direitos de utilização da Deja Platform são concedidos, validados e mantidos ao longo do ciclo de vida comercial de cada cliente.

O licenciamento é independente da implementação técnica dos módulos, constituindo uma camada institucional responsável por determinar a elegibilidade de uso de produtos, funcionalidades e capacidades.

---

## Objetivos

O modelo possui como objetivos:

- controlar a elegibilidade de utilização;
- suportar múltiplos modelos comerciais;
- permitir evolução sem impacto nos módulos;
- separar regras comerciais das regras técnicas;
- suportar operação SaaS e On-Premises;
- permitir licenciamento granular;
- suportar contratos corporativos.

---

## Hierarquia Comercial

O modelo adota a seguinte hierarquia institucional:

```
Organização
        │
        ▼
     Contrato
        │
        ▼
      Plano
        │
        ▼
   Assinatura
        │
        ▼
     Licença
        │
        ▼
 Tenant / Ambiente
        │
        ▼
 Produtos / Módulos / Capacidades
```

Cada nível adiciona informações específicas sem substituir as responsabilidades dos níveis anteriores.

---

## Licença

A Licença representa a autorização institucional de uso concedida a uma Organização ou Tenant.

Uma licença define:

- escopo autorizado;
- período de validade;
- plano associado;
- capacidades disponíveis;
- limites operacionais;
- restrições comerciais;
- políticas aplicáveis.

---

## Escopo de Licenciamento

O modelo suporta licenciamento em diferentes níveis:

- Plataforma completa;
- Produto;
- Módulo;
- Capability;
- Serviço;
- API;
- Feature;
- Recurso específico.

Novos níveis poderão ser adicionados futuramente sem alteração estrutural.

---

## Direitos de Uso

Cada licença concede direitos explícitos, como:

- executar funcionalidades;
- instalar módulos;
- consumir APIs;
- utilizar recursos premium;
- acessar ambientes específicos;
- utilizar capacidades adicionais.

Todos os direitos são avaliados pela camada de validação de elegibilidade.

---

## Restrições

Uma licença poderá impor restrições como:

- quantidade máxima de usuários;
- quantidade de Tenants;
- quantidade de Ambientes;
- limite de armazenamento;
- limite de processamento;
- limite de execuções;
- limite de chamadas de API;
- período de validade.

---

## Estados da Licença

Durante seu ciclo de vida, uma licença poderá assumir estados como:

- Provisionada;
- Ativa;
- Suspensa;
- Expirada;
- Cancelada;
- Revogada.

A mudança de estado gera eventos institucionais auditáveis.

---

## Renovação

O processo de renovação pode ocorrer:

- automaticamente;
- manualmente;
- mediante novo contrato;
- mediante alteração de plano.

A arquitetura não impõe um único modelo de renovação.

---

## Independência Tecnológica

Os módulos da plataforma nunca implementam regras de licenciamento.

Eles apenas consultam os serviços institucionais de Billing / Licensing para verificar sua elegibilidade antes da execução.

---

## Evolução

O modelo foi concebido para suportar a incorporação futura de novos formatos de comercialização, como:

- pay-per-use;
- assinatura híbrida;
- créditos de consumo;
- licenciamento por capacidade;
- marketplace de módulos;
- cobrança baseada em eventos.

Toda evolução deverá preservar compatibilidade com contratos e licenças previamente emitidos.