# Template de Cálculo

## Objetivo

Este documento define o modelo institucional oficial para documentação das regras de cálculo utilizadas pelos indicadores da Deja Indicadores.

Seu objetivo é garantir que todas as fórmulas, variáveis, transformações e critérios matemáticos sejam documentados de forma uniforme, independente da tecnologia utilizada na implementação.

Este documento complementa o **indicator-template.md** e deverá ser utilizado sempre que o cálculo do indicador exigir documentação detalhada.

---

# Identificação

| Campo | Valor |
|--------|-------|
| Indicador | IND-XXX |
| Nome | |
| Versão | |
| Status | Em Elaboração / Aprovado |

---

# Objetivo do Cálculo

Descrever qual resultado o cálculo produz e qual sua finalidade dentro do indicador.

---

# Fórmula Oficial

Documentar a fórmula matemática oficial.

```text
Resultado = ...
```

Sempre que possível utilizar notação matemática convencional.

---

# Variáveis

| Variável | Descrição | Origem | Tipo | Unidade |
|----------|-----------|---------|------|----------|
| | | | | |

---

# Regras de Negócio

Relacionar todas as regras que influenciam o cálculo.

Exemplos:

- registros considerados;
- exclusões;
- prioridades;
- condições especiais;
- arredondamentos.

---

# Agregações

Informar quais operações são utilizadas.

Exemplos:

- soma;
- média;
- média ponderada;
- máximo;
- mínimo;
- contagem;
- contagem distinta;
- percentil.

---

# Transformações

Descrever transformações realizadas antes ou após o cálculo.

Exemplos:

- normalização;
- conversão de unidades;
- cálculo percentual;
- índices;
- acumulados;
- projeções.

---

# Tratamento de Exceções

Documentar como o cálculo deverá tratar situações como:

- ausência de dados;
- valores nulos;
- divisão por zero;
- inconsistências;
- duplicidades;
- valores negativos inesperados.

---

# Precisão

Informar:

- número de casas decimais;
- regras de arredondamento;
- tolerâncias aceitáveis;
- unidade de medida.

---

# Dependências

Relacionar dependências necessárias para execução do cálculo.

Exemplos:

- fontes de dados;
- outros indicadores;
- serviços;
- APIs;
- componentes da plataforma.

---

# Exemplos

Apresentar exemplos práticos de cálculo.

## Exemplo 1

```text
Entradas:

Faturamento = 150.000
Quantidade = 500

Resultado:

Ticket Médio = 300
```

Adicionar quantos exemplos forem necessários para eliminar ambiguidades.

---

# Critérios de Validação

Relacionar os critérios mínimos para validação do cálculo.

Exemplos:

- reprodução da fórmula;
- conferência manual;
- comparação entre períodos;
- comportamento em limites;
- tratamento de exceções.

---

# Rastreabilidade

Relacionar os artefatos institucionais associados ao cálculo.

| Artefato | Identificador |
|----------|---------------|
| Indicator | |
| Functional Specification | |
| Technical Architecture | |
| Implementation Architecture | |
| Código | |
| Testes | |

---

# Histórico de Alterações

| Versão | Data | Alteração | Responsável |
|--------|------|-----------|-------------|
| 1.0 | | Criação | |