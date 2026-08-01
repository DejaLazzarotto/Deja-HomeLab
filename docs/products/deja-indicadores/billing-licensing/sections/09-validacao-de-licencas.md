# 09. Validação de Licenças

## Visão Geral

A validação de licenças estabelece o mecanismo institucional responsável por verificar a elegibilidade comercial para utilização dos recursos da Deja Platform.

Toda funcionalidade sujeita a controle comercial deve, obrigatoriamente, consultar o Billing / Licensing antes de sua execução.

A validação é centralizada no **Eligibility Service**, garantindo comportamento uniforme em toda a plataforma.

---

## Objetivos

O processo de validação possui os seguintes objetivos:

- verificar direitos de uso;
- impedir utilização não autorizada;
- aplicar regras comerciais de forma consistente;
- controlar limites operacionais;
- suportar múltiplos modelos de licenciamento;
- manter rastreabilidade integral das decisões.

---

## Fluxo Conceitual

```
Solicitação de Execução
           │
           ▼
Eligibility Service
           │
           ▼
Validação da Licença
           │
           ├── Contrato
           ├── Assinatura
           ├── Plano
           ├── Licença
           ├── Tenant
           ├── Ambiente
           ├── Limites
           ├── Consumo
           └── Políticas
           │
           ▼
Resultado da Elegibilidade
           │
     ┌─────┴─────┐
     ▼           ▼
Autorizado   Não Autorizado
```

---

## Critérios de Validação

A decisão de elegibilidade pode considerar, entre outros fatores:

- contrato vigente;
- assinatura ativa;
- licença válida;
- plano contratado;
- Tenant autorizado;
- ambiente permitido;
- recursos licenciados;
- limites operacionais;
- consumo acumulado;
- políticas comerciais;
- período de vigência.

A arquitetura permite que novos critérios sejam incorporados sem alterações estruturais.

---

## Resultado da Validação

A resposta do Eligibility Service pode conter:

- situação da validação;
- motivo da decisão;
- recursos autorizados;
- limites aplicáveis;
- restrições identificadas;
- data da validação;
- identificador da decisão.

Essas informações podem ser reutilizadas por outros componentes institucionais.

---

## Situações de Negativa

A validação poderá ser recusada por motivos como:

- licença inexistente;
- licença expirada;
- assinatura cancelada;
- contrato encerrado;
- limite de consumo excedido;
- recurso não contratado;
- ambiente não autorizado;
- Tenant inválido;
- política comercial impeditiva.

Cada negativa gera registro auditável.

---

## Cache de Elegibilidade

Para reduzir latência, a arquitetura permite a utilização de mecanismos de cache.

Entretanto:

- o cache não substitui a autoridade do Eligibility Service;
- deve respeitar tempo de expiração configurável;
- deve ser invalidado por eventos comerciais relevantes, como alteração de plano, renovação ou revogação de licença.

---

## Eventos de Validação

As decisões de elegibilidade podem originar eventos institucionais, como:

- licença validada;
- acesso autorizado;
- acesso negado;
- limite excedido;
- licença expirada;
- política aplicada.

Esses eventos podem ser consumidos por componentes como Observability, Audit, Security e Reporting.

---

## Integração com a Plataforma

Os módulos da Deja Platform não implementam lógica própria de licenciamento.

Eles apenas solicitam a validação ao Eligibility Service antes da execução de funcionalidades sujeitas a controle comercial.

Essa abordagem garante uniformidade, baixo acoplamento e facilidade de evolução.

---

## Auditoria

Toda validação permanece registrada com informações suficientes para reconstrução da decisão.

São preservados:

- contexto da solicitação;
- regras aplicadas;
- licença utilizada;
- resultado da validação;
- justificativa da decisão;
- data e hora;
- identificador da operação.

---

## Resultado Esperado

Ao centralizar a validação de licenças no Eligibility Service, a Deja Platform estabelece um mecanismo único, auditável, escalável e desacoplado para controle de elegibilidade comercial, assegurando que toda utilização da plataforma respeite as condições contratuais e de licenciamento definidas para cada Organização e Tenant.