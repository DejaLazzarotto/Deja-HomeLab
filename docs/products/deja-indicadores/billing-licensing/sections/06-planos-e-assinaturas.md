# 06. Planos e Assinaturas

## Visão Geral

Os Planos e Assinaturas representam a camada comercial responsável por definir quais capacidades da Deja Platform estão disponíveis para cada Organização e Tenant.

Enquanto o Plano descreve a oferta comercial, a Assinatura representa a contratação efetiva dessa oferta por um cliente.

Essa separação permite reutilização de planos, evolução das ofertas comerciais e flexibilidade contratual.

---

## Modelo Conceitual

```
Produto
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
Tenant
```

Cada elemento possui responsabilidades próprias e independentes.

---

## Plano

O Plano representa um modelo comercial reutilizável.

Um plano define, entre outros aspectos:

- capacidades disponíveis;
- módulos habilitados;
- limites operacionais;
- recursos opcionais;
- políticas comerciais;
- regras de consumo;
- regras de renovação;
- elegibilidade para funcionalidades.

Os planos não possuem vínculo direto com clientes específicos.

---

## Catálogo de Planos

O Billing / Licensing mantém um catálogo institucional de planos.

Exemplos de categorias:

- Community;
- Starter;
- Professional;
- Business;
- Enterprise;
- Corporate;
- Custom.

A nomenclatura dos planos não faz parte da arquitetura e pode evoluir conforme a estratégia comercial.

---

## Versionamento de Planos

Os planos são versionados.

Novas versões podem alterar:

- limites;
- funcionalidades;
- políticas;
- preços;
- recursos disponíveis.

Assinaturas existentes permanecem vinculadas à versão contratada até que ocorra migração explícita ou renovação contratual.

---

## Assinatura

A Assinatura representa a contratação de um plano por uma Organização ou Tenant.

Cada assinatura estabelece:

- plano contratado;
- período de vigência;
- ciclo de cobrança;
- contrato associado;
- estado atual;
- políticas aplicáveis.

---

## Estados da Assinatura

Durante seu ciclo de vida, uma assinatura pode assumir estados como:

- Provisionada;
- Ativa;
- Suspensa;
- Em Renovação;
- Expirada;
- Cancelada;
- Encerrada.

As transições de estado são registradas como eventos institucionais auditáveis.

---

## Ciclo de Vida

O ciclo típico de uma assinatura compreende:

1. contratação;
2. provisionamento;
3. ativação;
4. utilização;
5. renovação;
6. alteração de plano;
7. suspensão (quando aplicável);
8. encerramento.

Cada etapa gera registros rastreáveis.

---

## Upgrade e Downgrade

A arquitetura suporta alteração de planos durante a vigência contratual.

As políticas institucionais podem definir:

- aplicação imediata;
- aplicação na renovação;
- cobrança proporcional;
- período de carência;
- preservação de direitos adquiridos.

As regras específicas permanecem configuráveis pelo Commercial Policy Engine.

---

## Múltiplas Assinaturas

Uma Organização poderá possuir múltiplas assinaturas simultaneamente.

Exemplos:

- diferentes produtos;
- diferentes ambientes;
- módulos adicionais;
- planos complementares;
- contratos independentes.

Essa flexibilidade permite a composição de ofertas comerciais complexas sem aumentar o acoplamento arquitetural.

---

## Relação com Licenciamento

A assinatura não concede diretamente direitos de uso.

Ela fornece as informações comerciais necessárias para a emissão e manutenção das Licenças, que constituem a autorização efetiva para utilização da plataforma.

---

## Princípios

A arquitetura adota os seguintes princípios para planos e assinaturas:

- planos são modelos reutilizáveis;
- assinaturas representam contratos ativos;
- licenças derivam das assinaturas;
- alterações preservam rastreabilidade;
- políticas comerciais são centralizadas;
- múltiplas assinaturas são suportadas nativamente;
- evolução comercial ocorre sem impacto sobre os módulos da plataforma.

---

## Resultado Esperado

O modelo de Planos e Assinaturas estabelece uma base comercial flexível, escalável e desacoplada, capaz de suportar diferentes estratégias de monetização, múltiplos produtos e futuras evoluções da Deja Platform sem comprometer a estabilidade arquitetural.