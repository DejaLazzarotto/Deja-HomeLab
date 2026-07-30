# Catálogo de Indicadores

## Visão Geral

O Catálogo de Indicadores constitui a referência oficial para todos os indicadores analíticos suportados pela Deja Indicadores.

Seu objetivo é documentar, de forma padronizada, todas as definições necessárias para implementação, manutenção, evolução e validação dos indicadores disponibilizados pelo produto.

Cada indicador possui uma especificação própria contendo sua definição funcional, regras de cálculo, parâmetros, filtros, fontes de dados, requisitos de implementação, visualizações suportadas e rastreabilidade completa.

Esta documentação atua como elo entre as Especificações Funcionais, a Arquitetura Técnica e a implementação do produto.

---

# Objetivos

O Catálogo de Indicadores possui como principais objetivos:

- padronizar a definição dos indicadores;
- eliminar ambiguidades nas regras de cálculo;
- garantir consistência entre diferentes implementações;
- facilitar evolução e manutenção;
- apoiar validações funcionais;
- apoiar testes automatizados;
- servir como documentação oficial para equipes técnicas e funcionais;
- garantir rastreabilidade institucional.

---

# Estrutura

A organização desta documentação segue o padrão institucional da Deja Platform.

```text
indicator-catalog/

├── README.md
├── indicator-catalog-v1.md
├── indicators/
├── shared/
└── sections/
```

Onde:

- **README.md** apresenta a visão geral do catálogo;
- **indicator-catalog-v1.md** representa o Documento Mestre;
- **sections/** contém a documentação institucional do catálogo;
- **shared/** concentra componentes reutilizáveis entre indicadores;
- **indicators/** contém a documentação individual de cada indicador.

---

# Organização dos Indicadores

Cada indicador deverá possuir um diretório próprio contendo toda sua documentação.

Exemplo:

```text
indicators/

├── IND-001-faturamento/
├── IND-002-ticket-medio/
├── IND-003-margem/
└── ...
```

Cada diretório será independente e possuirá toda a documentação necessária para aquele indicador.

---

# Integração com a Documentação

O Catálogo de Indicadores integra-se diretamente com:

- Product Vision;
- Product Architecture;
- Capability Map;
- Value Backlog;
- Functional Architecture;
- Functional Specifications;
- Technical Architecture;
- Implementation Architecture.

Cada indicador deverá possuir rastreabilidade completa com sua origem funcional e técnica.

---

# Rastreabilidade

A cadeia institucional permanece:

```text
CAP
 ↓
EP
 ↓
FM
 ↓
FE
 ↓
FF
 ↓
FS
 ↓
Arquitetura Técnica
 ↓
Arquitetura de Implementação
 ↓
Indicador
 ↓
Código
 ↓
Testes
 ↓
Documentação
```

---

# Evolução

O Catálogo de Indicadores é um documento vivo.

Novos indicadores poderão ser incorporados sem alterar a organização institucional da documentação.

Toda alteração deverá preservar compatibilidade, rastreabilidade e governança estabelecidas pela Deja Platform.