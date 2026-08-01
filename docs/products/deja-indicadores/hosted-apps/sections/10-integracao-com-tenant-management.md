# 10. Integração com Tenant Management

## Visão Geral

A Hosted Apps integra-se à capacidade Tenant Management para garantir que toda aplicação hospedada seja executada dentro de um contexto institucional válido, preservando isolamento, governança e administração dos recursos da Deja Platform.

O Tenant Management permanece como a única autoridade responsável pela gestão de organizações, tenants, ambientes e contexto de execução.

A Hosted Apps consome exclusivamente os contratos públicos disponibilizados por essa capacidade.

---

## Objetivos da Integração

A integração possui os seguintes objetivos:

- identificar a organização proprietária da aplicação
- determinar o tenant de execução
- resolver o ambiente operacional
- validar o contexto institucional
- preservar isolamento entre tenants
- suportar ambientes independentes
- garantir consistência operacional

---

## Contexto Institucional

Antes da implantação ou execução de uma aplicação, a Hosted Apps obtém do Tenant Management informações como:

- organização
- tenant
- ambiente
- contexto de execução
- identificadores institucionais
- políticas aplicáveis

Esse contexto acompanha todas as operações realizadas sobre a aplicação.

---

## Isolamento entre Tenants

Cada aplicação é executada dentro do tenant ao qual foi associada.

A Hosted Apps garante que:

- recursos não sejam compartilhados entre tenants sem autorização
- configurações permaneçam isoladas
- estados operacionais sejam independentes
- operações administrativas respeitem o contexto institucional

---

## Ambientes

A Hosted Apps utiliza os ambientes definidos pelo Tenant Management para controlar onde cada aplicação pode ser implantada.

Exemplos:

- desenvolvimento
- homologação
- produção
- ambientes privados
- ambientes dedicados

Cada ambiente possui políticas próprias de operação e deployment.

---

## Provisionamento

Durante o processo de implantação, a Hosted Apps consulta o Tenant Management para validar:

- existência da organização
- tenant de destino
- ambiente autorizado
- contexto de execução
- políticas institucionais vigentes

Somente após essas validações a implantação pode prosseguir.

---

## Administração

As operações administrativas realizadas pela Hosted Apps respeitam integralmente os limites definidos pelo Tenant Management.

Isso inclui:

- escopo organizacional
- limites do tenant
- ambientes autorizados
- permissões institucionais

---

## Integração por Contratos Públicos

Toda comunicação entre Hosted Apps e Tenant Management ocorre exclusivamente por contratos públicos.

Não existe acesso direto às estruturas internas da capacidade Tenant Management.

Essa abordagem preserva desacoplamento, evolução independente e estabilidade arquitetural.

---

## Benefícios Arquiteturais

A integração com Tenant Management garante:

- isolamento institucional
- consistência entre ambientes
- governança centralizada
- execução contextualizada
- administração segura
- escalabilidade multi-tenant
- compatibilidade evolutiva da Deja Platform