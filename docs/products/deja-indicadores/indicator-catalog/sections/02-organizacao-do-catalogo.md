# Organização do Catálogo

## Objetivo

Este documento define a organização institucional do Catálogo Oficial de Indicadores da Deja Indicadores.

Seu objetivo é estabelecer uma estrutura padronizada para documentação, evolução e manutenção dos indicadores analíticos do produto, garantindo consistência, rastreabilidade e facilidade de expansão.

---

# Organização Geral

O Catálogo de Indicadores está organizado em três componentes principais:

```text
indicator-catalog/

├── indicators/
├── shared/
└── sections/
```

Cada componente possui responsabilidades específicas e complementares.

---

# Diretório indicators/

O diretório **indicators/** concentra a documentação individual de todos os indicadores suportados pelo produto.

Cada indicador deverá possuir um diretório exclusivo.

Exemplo:

```text
indicators/

├── IND-001-faturamento/
├── IND-002-ticket-medio/
├── IND-003-lucratividade/
├── IND-004-margem-contribuicao/
└── ...
```

Essa organização permite que cada indicador evolua independentemente, preservando sua documentação histórica e facilitando futuras ampliações.

---

# Estrutura de um Indicador

Cada diretório de indicador deverá seguir uma organização padronizada.

Exemplo:

```text
IND-001-faturamento/

├── README.md
├── indicator.md
├── calculation.md
├── implementation.md
├── tests.md
└── changelog.md
```

Essa estrutura poderá ser evoluída futuramente, mantendo compatibilidade com os padrões institucionais definidos neste catálogo.

---

# Diretório shared/

O diretório **shared/** reúne componentes documentais reutilizáveis entre diferentes indicadores.

Entre os componentes compartilhados poderão estar:

- modelos de documentação;
- glossário institucional;
- convenções de nomenclatura;
- padrões de cálculo;
- padrões de visualização;
- modelos de testes;
- componentes reutilizáveis de rastreabilidade.

Essa abordagem reduz duplicidade e facilita a manutenção da documentação.

---

# Diretório sections/

O diretório **sections/** contém os documentos institucionais que descrevem a arquitetura e a organização do Catálogo de Indicadores.

Esses documentos definem os padrões que deverão ser observados por todos os indicadores documentados.

---

# Identificação dos Indicadores

Cada indicador deverá possuir um identificador institucional único.

Formato recomendado:

```text
IND-001
IND-002
IND-003
...
```

O identificador deverá permanecer imutável durante todo o ciclo de vida do indicador, independentemente de alterações em seu nome ou descrição.

---

# Padronização

Todos os indicadores deverão seguir exatamente a mesma estrutura documental.

Não serão admitidos formatos específicos para indicadores isolados, salvo quando formalmente aprovados pela governança do produto.

A padronização assegura:

- facilidade de navegação;
- consistência documental;
- reutilização de componentes;
- simplificação das revisões;
- automação futura da documentação.

---

# Evolução

A organização do catálogo foi concebida para permitir crescimento contínuo.

Novos indicadores poderão ser adicionados sem necessidade de reorganizar a estrutura existente.

Essa característica preserva a estabilidade da documentação, facilita o versionamento e garante escalabilidade para futuras versões da Deja Indicadores.