# 08. Lineage

## Objetivo

Esta seção define a arquitetura institucional de Lineage do Data Store.

O Lineage é responsável por registrar, preservar e disponibilizar as relações existentes entre os ativos persistidos pela plataforma, permitindo compreender sua origem, evolução, dependências e impacto ao longo de todo o ciclo de vida.

---

# Conceito

Lineage representa o histórico completo das relações entre os ativos da Deja Indicadores.

Seu objetivo é responder perguntas como:

- De onde este Dataset foi originado?
- Quais transformações foram aplicadas?
- Quais versões participaram do processamento?
- Quais indicadores utilizam este Dataset?
- Quais diagnósticos dependem deste ativo?
- Quais recomendações foram produzidas a partir dele?

O Lineage constitui uma capacidade arquitetural obrigatória do Data Store.

---

# Princípios

O modelo institucional de Lineage baseia-se nos seguintes princípios:

- registro automático;
- rastreabilidade completa;
- independência da tecnologia;
- versionamento das relações;
- imutabilidade dos registros históricos;
- consulta eficiente;
- integração com auditoria.

Esses princípios garantem a preservação do conhecimento sobre a evolução dos ativos.

---

# Relações Registradas

O Lineage registra diferentes tipos de relacionamento, incluindo:

- origem dos dados;
- transformações realizadas;
- dependências entre ativos;
- versões relacionadas;
- publicações;
- consumo pelos componentes da plataforma;
- geração de artefatos;
- substituições de versões.

Cada relacionamento representa uma ligação explícita entre dois ou mais ativos institucionais.

---

# Grafo Institucional

O conjunto de registros de Lineage forma um grafo institucional de dependências.

Esse grafo permite:

- navegar entre ativos relacionados;
- identificar impactos de alterações;
- reconstruir cadeias completas de processamento;
- compreender a evolução dos dados ao longo do tempo.

O modelo lógico do grafo permanece independente da implementação física.

---

# Integração com o Data Pipeline

O Data Pipeline informa ao Data Store todas as relações produzidas durante o processamento.

Entre elas:

- fontes de origem;
- etapas executadas;
- Datasets produzidos;
- versões geradas;
- publicações realizadas.

O Data Store torna essas relações persistentes e consultáveis.

---

# Integração com o Intelligence Core

O Intelligence Core amplia o Lineage ao registrar relações entre:

- Datasets;
- Indicadores;
- Diagnósticos;
- Decisões;
- Recomendações;
- Artefatos analíticos.

Dessa forma, o Lineage ultrapassa a camada de dados e cobre todo o ecossistema de inteligência.

---

# Relação com o Versionamento

Cada versão de um ativo possui seus próprios registros de Lineage.

Isso garante que seja possível reconstruir exatamente:

- quais entradas foram utilizadas;
- quais versões participaram do processamento;
- quais resultados foram produzidos.

Esse princípio assegura reprodutibilidade completa.

---

# Consulta

Os registros de Lineage poderão ser consultados por diferentes critérios, como:

- ativo;
- versão;
- origem;
- destino;
- período;
- tipo de relacionamento;
- componente produtor.

Os mecanismos de consulta são definidos pelos contratos públicos do Data Store.

---

# Auditoria

Os registros de Lineage constituem uma das principais fontes para auditoria institucional.

Eles permitem:

- reconstrução histórica;
- investigação de incidentes;
- análise de impacto;
- comprovação de origem;
- validação de conformidade;
- suporte à governança.

---

# Benefícios

O modelo institucional de Lineage proporciona:

- rastreabilidade ponta a ponta;
- transparência do processamento;
- análise de impacto;
- auditoria completa;
- reprodutibilidade;
- governança dos ativos;
- preservação do conhecimento operacional;
- integração consistente entre os componentes da plataforma.

---

# Próxima Seção

A próxima seção apresenta a arquitetura de persistência dos Artefatos de Execução, responsáveis por armazenar os produtos gerados durante os diferentes processos do ecossistema da Deja Indicadores.