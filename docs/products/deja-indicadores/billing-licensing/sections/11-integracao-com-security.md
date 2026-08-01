# 11. Integração com Security

## Visão Geral

O Billing / Licensing integra-se ao componente institucional de Security para garantir que autenticação, autorização e elegibilidade comercial permaneçam responsabilidades independentes e complementares.

Enquanto o Security verifica **quem** pode acessar a plataforma e **o que** está autorizado a fazer sob a perspectiva de identidade e permissões, o Billing / Licensing determina **se** aquele recurso está comercialmente disponível de acordo com contratos, planos, assinaturas e licenças.

Essa separação elimina acoplamento entre regras de segurança e regras comerciais.

---

## Responsabilidades

### Security

Compete ao Security:

- autenticar identidades;
- autorizar operações;
- gerenciar credenciais;
- controlar papéis (Roles);
- controlar permissões (Permissions);
- aplicar políticas de acesso;
- registrar eventos de segurança.

---

### Billing / Licensing

Compete ao Billing / Licensing:

- validar elegibilidade comercial;
- verificar licenças;
- validar assinaturas;
- controlar consumo;
- aplicar limites comerciais;
- determinar direitos contratados.

---

## Fluxo Conceitual

```
Usuário
    │
    ▼
Authentication
    │
    ▼
Authorization
    │
    ▼
Tenant Context
    │
    ▼
Eligibility Service
    │
    ▼
Execução da Funcionalidade
```

A funcionalidade somente poderá ser executada quando todas as etapas forem aprovadas.

---

## Ordem de Validação

A sequência institucional recomendada é:

1. autenticação;
2. autorização;
3. resolução do Tenant Context;
4. validação de elegibilidade comercial;
5. execução da operação.

Cada etapa é independente da anterior, porém todas são obrigatórias.

---

## Elegibilidade Comercial

O Eligibility Service pode validar, entre outros aspectos:

- licença vigente;
- plano contratado;
- assinatura ativa;
- recursos disponíveis;
- limites operacionais;
- ambiente autorizado;
- consumo acumulado;
- políticas comerciais.

A validação não substitui a autorização concedida pelo Security.

---

## Complementaridade

As responsabilidades permanecem claramente separadas.

Exemplos:

| Situação | Security | Billing / Licensing |
|----------|----------|---------------------|
| Usuário autenticado | ✔ | — |
| Permissão para executar ação | ✔ | — |
| Plano permite o recurso | — | ✔ |
| Licença válida | — | ✔ |
| Limite contratado disponível | — | ✔ |
| Consumo dentro da franquia | — | ✔ |

Essa separação permite evolução independente de ambos os componentes.

---

## Eventos Compartilhados

A integração pode utilizar eventos institucionais como:

- User Authenticated;
- User Authorization Granted;
- User Authorization Denied;
- License Validated;
- License Denied;
- Subscription Changed;
- Consumption Limit Reached.

Os eventos enriquecem processos de auditoria, observabilidade e rastreabilidade.

---

## Auditoria

As decisões de Security e Billing / Licensing permanecem registradas de forma independente, permitindo reconstruir integralmente o fluxo de autorização técnica e elegibilidade comercial.

A rastreabilidade conjunta facilita investigações, conformidade regulatória e suporte operacional.

---

## Princípios de Integração

A integração adota os seguintes princípios:

- autenticação não concede direitos comerciais;
- autorização não substitui licenciamento;
- elegibilidade comercial não substitui controle de acesso;
- decisões permanecem desacopladas;
- comunicação ocorre por contratos institucionais e eventos;
- toda decisão relevante deve ser auditável.

---

## Resultado Esperado

A integração entre Security e Billing / Licensing estabelece uma arquitetura em que identidade, permissões e direitos comerciais são tratados como domínios independentes, garantindo maior segurança, flexibilidade e capacidade de evolução da Deja Platform.