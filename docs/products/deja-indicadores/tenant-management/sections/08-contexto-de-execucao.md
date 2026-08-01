# 8. Contexto de Execução

## Objetivo

Esta seção define o modelo institucional de Contexto de Execução (Tenant Context) da Deja Platform.

O Contexto de Execução representa o conjunto de informações que identifica, durante uma operação, a Organização, o Tenant e o Ambiente ativos, permitindo que todos os componentes da plataforma executem suas responsabilidades de forma consistente, segura e rastreável.

---

# Conceito

Toda operação realizada na Deja Platform ocorre dentro de um contexto organizacional.

Esse contexto identifica de forma explícita onde a operação está sendo executada e quais recursos institucionais podem ser utilizados.

Nenhum componente poderá executar operações sem um Contexto de Execução válido.

---

# Tenant Context

O Tenant Context é o objeto institucional utilizado para representar o contexto ativo de uma execução.

Como regra mínima, ele deverá conter:

- Organization Identifier;
- Tenant Identifier;
- Environment Identifier;
- Context Identifier;
- Context Version.

Informações adicionais poderão ser incorporadas conforme evolução da plataforma.

---

# Ciclo de Vida do Contexto

O Contexto de Execução é criado no início de cada operação e permanece válido apenas durante sua execução.

O ciclo é composto pelas etapas:

```text
Recepção da Solicitação
            │
            ▼
Resolução do Contexto
            │
            ▼
Validação
            │
            ▼
Propagação
            │
            ▼
Execução
            │
            ▼
Finalização
            │
            ▼
Descarte
```

Após o término da operação, o Contexto é descartado.

---

# Resolução do Contexto

A resolução do Contexto é responsabilidade do **Tenant Context Resolver**.

O processo poderá utilizar informações provenientes de:

- autenticação;
- API Gateway;
- chamadas internas;
- eventos;
- workflows;
- filas;
- mensagens;
- integrações externas.

O resultado deverá ser um Tenant Context válido e consistente.

---

# Propagação

Após sua resolução, o Contexto deverá ser propagado por toda a cadeia de execução.

Todos os componentes consumidores utilizarão exatamente o mesmo Tenant Context durante a operação.

Nenhum componente poderá alterar o Contexto recebido.

Caso seja necessária uma mudança de contexto, uma nova operação deverá ser iniciada.

---

# Consistência

Durante a execução:

- o Contexto é imutável;
- todos os componentes compartilham a mesma referência lógica;
- alterações não são permitidas;
- inconsistências invalidam a operação.

Esse modelo garante previsibilidade e reduz riscos de processamento em contexto incorreto.

---

# Utilização pelos Componentes

O Tenant Context é consumido por diversos componentes institucionais, incluindo:

- Security;
- Configuration;
- API Gateway;
- API Management;
- Observability;
- Execution Engine;
- Execution History;
- Execution Log;
- Marketplace;
- Module Platform;
- Developer Portal.

Cada componente utiliza o Contexto exclusivamente para identificar o domínio organizacional da operação.

---

# Segurança

O Tenant Context não substitui autenticação ou autorização.

Essas responsabilidades permanecem no componente Security.

O Contexto apenas identifica o escopo organizacional da operação.

Toda validação de identidade, permissões e credenciais ocorre antes da criação do Tenant Context.

---

# Auditoria e Rastreabilidade

Toda criação e utilização de um Contexto de Execução deverá ser passível de rastreamento.

Os seguintes eventos deverão ser registrados:

- criação;
- resolução;
- validação;
- utilização;
- encerramento;
- falhas de resolução.

Os registros são produzidos pelos componentes institucionais de auditoria e observabilidade.

---

# Benefícios

A institucionalização do Contexto de Execução proporciona:

- consistência operacional;
- propagação padronizada do contexto;
- redução de acoplamento;
- isolamento organizacional;
- rastreabilidade completa;
- integração uniforme entre componentes;
- preparação para escalabilidade distribuída.

---

# Resultado Esperado

Ao final desta definição, toda operação realizada na Deja Platform ocorrerá obrigatoriamente dentro de um Contexto de Execução institucional, garantindo que Organização, Tenant e Ambiente sejam identificados de forma consistente durante todo o ciclo operacional da plataforma.