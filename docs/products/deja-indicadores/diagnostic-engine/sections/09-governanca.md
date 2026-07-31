# 09. Governança

## Objetivo

Este documento estabelece o modelo de governança do Diagnostic Engine da Deja Indicadores.

Seu objetivo é definir as políticas institucionais para criação, evolução, aprovação, versionamento, utilização e descontinuação das definições diagnósticas, garantindo consistência, rastreabilidade e preservação do patrimônio intelectual da plataforma.

---

# 1. Princípios de Governança

A governança do Diagnostic Engine baseia-se nos seguintes princípios:

* diagnósticos são ativos corporativos;
* definições possuem ciclo de vida próprio;
* alterações devem ser controladas;
* toda evolução deve ser documentada;
* rastreabilidade é obrigatória;
* compatibilidade histórica deve ser preservada;
* responsabilidades devem ser claramente definidas.

Toda alteração significativa deve possuir justificativa registrada.

---

# 2. Unidade Governada

A menor unidade de governança do Diagnostic Engine é a **Diagnostic Definition**.

Cada definição representa um ativo institucional independente e deve possuir:

* identificador único;
* nome;
* descrição;
* objetivo;
* domínio;
* versão;
* estado;
* responsáveis;
* histórico de alterações.

As regras associadas também são ativos governados e versionados.

---

# 3. Ciclo de Vida

Toda definição diagnóstica percorre o seguinte ciclo de vida institucional:

```text id="de-life-cycle"
Draft
   │
   ▼
Review
   │
   ▼
Approved
   │
   ▼
Active
   │
   ▼
Deprecated
   │
   ▼
Archived
```

### Draft

Definição em elaboração.

Ainda não pode ser utilizada em avaliações oficiais.

---

### Review

Definição submetida para revisão técnica e funcional.

Pode sofrer alterações antes da aprovação.

---

### Approved

Definição validada institucionalmente.

Está apta para publicação.

---

### Active

Definição disponível para utilização pelo Diagnostic Engine.

Somente definições ativas podem produzir diagnósticos oficiais.

---

### Deprecated

Definição substituída por outra versão mais recente.

Permanece disponível apenas para manutenção da rastreabilidade histórica.

---

### Archived

Definição retirada do uso operacional e preservada exclusivamente para fins históricos e auditoria.

---

# 4. Versionamento

Cada alteração relevante gera uma nova versão da definição diagnóstica.

O versionamento deve preservar:

* compatibilidade histórica;
* rastreabilidade;
* documentação;
* histórico de aprovação;
* referências utilizadas.

Diagnósticos emitidos permanecem vinculados à versão vigente no momento da execução.

---

# 5. Responsabilidades

Cada definição deve possuir responsáveis claramente identificados.

Entre os papéis institucionais destacam-se:

* responsável funcional;
* responsável técnico;
* aprovador institucional;
* mantenedor.

A atribuição de responsabilidades garante controle sobre a evolução do componente.

---

# 6. Gestão das Regras

As regras diagnósticas seguem o mesmo modelo de governança das definições.

Cada regra deve possuir:

* identificador;
* versão;
* estado;
* documentação;
* histórico;
* justificativa para alterações.

Regras reutilizadas por múltiplas definições devem preservar compatibilidade entre versões.

---

# 7. Revisões

As definições diagnósticas devem ser revisadas periodicamente.

A revisão pode ocorrer em função de:

* alterações regulatórias;
* mudanças organizacionais;
* evolução metodológica;
* novos indicadores;
* novos conhecimentos registrados na Knowledge Base;
* melhoria das interpretações diagnósticas.

Toda revisão deve ser documentada.

---

# 8. Auditoria

O processo de governança deve permitir verificar:

* quem criou a definição;
* quem aprovou;
* quando entrou em vigor;
* quando foi revisada;
* quais versões existiram;
* quais regras foram alteradas;
* quais diagnósticos utilizaram cada versão.

Essas informações devem permanecer disponíveis durante todo o ciclo de vida do ativo.

---

# 9. Integração com o Núcleo de Inteligência

A governança do Diagnostic Engine deve permanecer alinhada com os demais componentes do Núcleo de Inteligência.

Em especial:

* Indicator Catalog;
* Knowledge Base;
* Recommendation Engine;
* AI Assistant.

A evolução de um componente não deve comprometer a estabilidade dos contratos institucionais dos demais.

---

# 10. Evolução Controlada

A expansão do Diagnostic Engine deverá ocorrer de forma incremental.

Novas capacidades somente poderão ser incorporadas quando:

* preservarem compatibilidade arquitetural;
* mantiverem rastreabilidade;
* respeitarem os contratos públicos;
* forem devidamente documentadas;
* forem aprovadas institucionalmente.

Esse processo garante estabilidade e previsibilidade para toda a plataforma.

---

# Síntese

A governança do Diagnostic Engine assegura que definições diagnósticas, regras e avaliações sejam tratadas como ativos corporativos permanentes.

Ao estabelecer políticas de ciclo de vida, versionamento, revisão, auditoria e responsabilidades, a Deja Indicadores garante que o processo diagnóstico permaneça consistente, auditável e sustentável ao longo da evolução do Núcleo de Inteligência.
