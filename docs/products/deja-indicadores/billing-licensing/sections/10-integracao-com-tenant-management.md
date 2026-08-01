# 10. Integração com Tenant Management

## Visão Geral

O Billing / Licensing integra-se ao Tenant Management para associar contratos, assinaturas, licenças e consumo às estruturas organizacionais da Deja Platform.

Enquanto o Tenant Management é responsável pela gestão de Organizações, Tenants, Ambientes e Contexto de Execução, o Billing / Licensing determina os direitos comerciais e a elegibilidade de utilização desses elementos.

Essa separação preserva o desacoplamento entre a estrutura organizacional e o modelo comercial da plataforma.

---

## Responsabilidades

### Tenant Management

Compete ao Tenant Management:

- gerenciar Organizações;
- gerenciar Tenants;
- gerenciar Ambientes;
- fornecer o Tenant Context;
- garantir isolamento organizacional;
- disponibilizar informações cadastrais.

---

### Billing / Licensing

Compete ao Billing / Licensing:

- gerenciar contratos;
- gerenciar planos;
- gerenciar assinaturas;
- emitir licenças;
- validar elegibilidade;
- controlar consumo;
- consolidar faturamento.

---

## Modelo de Integração

```
Organização
      │
      ▼
Tenant Management
      │
      ▼
Tenant
      │
      ▼
Ambiente
      │
      ▼
Billing / Licensing
      │
      ├── Contrato
      ├── Plano
      ├── Assinatura
      ├── Licença
      ├── Consumo
      └── Elegibilidade
```

Cada componente permanece responsável exclusivamente por seu domínio.

---

## Organização

As Organizações representam a entidade administrativa responsável pela relação comercial com a Deja Platform.

Uma Organização pode:

- possuir múltiplos Tenants;
- manter múltiplos contratos;
- contratar diferentes planos;
- possuir diversas assinaturas;
- administrar diferentes ambientes de operação.

---

## Tenant

O Tenant representa a unidade oficial de isolamento operacional da plataforma.

As licenças podem ser concedidas:

- para um Tenant específico;
- para múltiplos Tenants da mesma Organização;
- para toda a Organização, conforme as políticas comerciais aplicáveis.

---

## Ambientes

Os Ambientes pertencem ao Tenant e representam contextos operacionais independentes, como:

- Desenvolvimento;
- Homologação;
- Produção;
- Treinamento;
- Laboratório.

As políticas comerciais podem definir direitos distintos para cada ambiente.

---

## Tenant Context

Toda solicitação processada pela plataforma deve conter um Tenant Context válido.

Esse contexto é utilizado pelo Billing / Licensing para:

- localizar contratos;
- identificar assinaturas;
- validar licenças;
- consultar limites;
- registrar consumo;
- consolidar faturamento.

---

## Provisionamento

Quando um novo Tenant é criado, o Tenant Management publica eventos institucionais que podem ser consumidos pelo Billing / Licensing para:

- iniciar o provisionamento comercial;
- criar estruturas de consumo;
- associar contratos existentes;
- emitir licenças iniciais;
- aplicar políticas padrão.

Da mesma forma, alterações ou remoções de Tenants podem gerar atualizações no domínio comercial.

---

## Sincronização por Eventos

A integração ocorre preferencialmente por eventos institucionais.

Exemplos:

- Organization Created;
- Tenant Created;
- Tenant Updated;
- Tenant Removed;
- Environment Created;
- Environment Removed.

Esses eventos permitem que o Billing / Licensing mantenha suas informações sincronizadas sem dependência direta do Tenant Management.

---

## Princípios de Integração

A integração observa os seguintes princípios:

- separação entre estrutura organizacional e regras comerciais;
- comunicação por contratos institucionais e eventos;
- ausência de dependências circulares;
- preservação do Tenant como unidade oficial de isolamento;
- desacoplamento entre provisionamento e faturamento.

---

## Resultado Esperado

A integração entre Tenant Management e Billing / Licensing estabelece uma base consistente para operação comercial da Deja Platform, permitindo que contratos, licenças, consumo e faturamento sejam aplicados de forma segura, rastreável e escalável sobre a estrutura organizacional definida pelo Tenant Management.