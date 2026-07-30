# Template de Indicador

## Objetivo

Este documento define o modelo institucional oficial para documentação dos indicadores da Deja Indicadores.

Todo indicador deverá utilizar obrigatoriamente este template, garantindo padronização, rastreabilidade e consistência entre as documentações.

---

# Identificação

| Campo | Valor |
|--------|-------|
| Identificador | IND-XXX |
| Nome | |
| Categoria | |
| Domínio de Negócio | |
| Versão | |
| Status | Proposto / Em Revisão / Aprovado / Implementado / Descontinuado |

---

# Objetivo

Descrever claramente qual problema de negócio o indicador resolve e qual decisão ele apoia.

---

# Descrição Funcional

Explicar o comportamento esperado do indicador utilizando linguagem de negócio.

Evitar detalhes de implementação.

---

# Contexto de Utilização

Informar:

- quando utilizar;
- quem utiliza;
- em quais dashboards poderá aparecer;
- restrições conhecidas.

---

# Regras de Negócio

Descrever todas as regras que influenciam o cálculo e a interpretação do indicador.

---

# Fórmula

Documentar a fórmula matemática oficial.

```text
Resultado = ...
```

Quando necessário, referenciar o documento de cálculo correspondente.

---

# Variáveis

| Variável | Descrição | Origem | Unidade |
|----------|-----------|---------|----------|
| | | | |

---

# Fontes de Dados

Relacionar todas as fontes utilizadas.

| Fonte | Descrição |
|--------|-----------|
| | |

---

# Parâmetros

Listar os parâmetros aceitos pelo indicador.

Exemplos:

- período;
- empresa;
- filial;
- vendedor;
- cliente;
- produto.

---

# Dimensões Analíticas

Relacionar as dimensões suportadas.

Exemplos:

- tempo;
- região;
- unidade;
- categoria;
- segmento.

---

# Filtros Suportados

Relacionar todos os filtros que podem alterar o resultado apresentado.

---

# Periodicidade

Informar a periodicidade do cálculo.

Exemplos:

- tempo real;
- diário;
- semanal;
- mensal.

---

# Visualizações Recomendadas

Indicar as formas de apresentação mais adequadas.

Exemplos:

- Cartão de KPI;
- Gráfico de Barras;
- Gráfico de Linhas;
- Série Temporal;
- Ranking.

---

# Tratamento de Exceções

Documentar como o indicador deverá se comportar em situações como:

- ausência de dados;
- valores nulos;
- divisão por zero;
- inconsistências;
- registros duplicados.

---

# Requisitos de Implementação

Relacionar:

- serviços necessários;
- APIs;
- componentes;
- dependências;
- requisitos de desempenho;
- requisitos de segurança.

---

# Critérios de Teste

Definir os testes mínimos para validação.

Exemplos:

- cálculo correto;
- consistência entre filtros;
- tratamento de exceções;
- desempenho;
- estabilidade.

---

# Rastreabilidade

Relacionar os artefatos institucionais.

| Artefato | Identificador |
|----------|---------------|
| Capability | |
| Epic | |
| Functional Module | |
| Feature | |
| Functional Flow | |
| Functional Specification | |
| Technical Architecture | |
| Implementation Architecture | |

---

# Histórico de Alterações

| Versão | Data | Alteração | Responsável |
|--------|------|-----------|-------------|
| 1.0 | | Criação | |