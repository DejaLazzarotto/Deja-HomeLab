# Cálculos

## Objetivo

Este documento estabelece as diretrizes institucionais para documentação dos cálculos utilizados pelos indicadores da Deja Indicadores.

Seu objetivo é garantir que todas as regras matemáticas, agregações, transformações e critérios de processamento sejam especificados de forma clara, consistente e independente da tecnologia empregada na implementação.

---

# Princípios

Todo cálculo deverá:

- possuir definição explícita;
- utilizar nomenclatura padronizada;
- ser determinístico;
- produzir resultados reproduzíveis;
- possuir documentação completa;
- permitir auditoria;
- permanecer independente da linguagem de programação.

A documentação do cálculo representa a referência oficial para todas as implementações.

---

# Definição do Cálculo

Cada indicador deverá apresentar sua regra de cálculo de forma estruturada.

A documentação deverá conter:

- objetivo do cálculo;
- descrição conceitual;
- fórmula matemática;
- significado de cada variável;
- unidade de medida;
- resultado esperado.

Sempre que possível, a fórmula deverá utilizar notação matemática convencional.

---

# Variáveis

Todas as variáveis utilizadas deverão ser documentadas.

Para cada variável deverão ser informados:

- nome;
- descrição;
- origem;
- tipo de dado;
- unidade;
- obrigatoriedade;
- regras de validação.

Essa documentação evita interpretações divergentes durante a implementação.

---

# Agregações

Quando houver consolidação de informações, deverão ser especificados os métodos de agregação utilizados.

Exemplos:

- soma;
- média;
- média ponderada;
- contagem;
- contagem distinta;
- máximo;
- mínimo;
- mediana;
- percentil;
- desvio padrão;
- variância.

O método adotado deverá permanecer explícito na documentação.

---

# Transformações

Quando os dados exigirem processamento adicional, as transformações deverão ser descritas.

Exemplos:

- conversão de unidades;
- normalização;
- padronização;
- arredondamentos;
- cálculo percentual;
- cálculo acumulado;
- índices;
- projeções;
- comparação entre períodos.

As transformações deverão ocorrer em ordem claramente definida.

---

# Tratamento de Exceções

Todo cálculo deverá definir o comportamento esperado diante de situações excepcionais.

Entre elas:

- ausência de dados;
- valores nulos;
- divisão por zero;
- registros duplicados;
- inconsistências de origem;
- valores negativos inesperados;
- dados fora do intervalo permitido.

As regras de tratamento deverão ser documentadas para garantir resultados previsíveis.

---

# Precisão Numérica

Sempre que aplicável, deverão ser definidos:

- número de casas decimais;
- regras de arredondamento;
- precisão mínima;
- tolerâncias aceitáveis;
- tratamento de perdas de precisão.

Esses critérios asseguram uniformidade entre diferentes ambientes de execução.

---

# Periodicidade do Cálculo

A documentação deverá informar quando o cálculo é executado.

Exemplos:

- em tempo real;
- sob demanda;
- diariamente;
- semanalmente;
- mensalmente;
- durante processos de consolidação;
- após importações de dados.

Essa informação influencia diretamente a interpretação dos resultados.

---

# Validação

Todo cálculo deverá possuir critérios objetivos para validação.

Os testes deverão verificar, sempre que aplicável:

- correção matemática;
- consistência entre períodos;
- consistência entre filtros;
- comportamento em limites;
- tratamento de exceções;
- estabilidade dos resultados.

Os critérios definidos nesta documentação servirão de base para os testes automatizados.

---

# Rastreabilidade

Cada cálculo deverá manter vínculo explícito com:

- indicador correspondente;
- regras de negócio;
- especificações funcionais;
- fontes de dados utilizadas;
- componentes responsáveis pela implementação;
- testes automatizados.

Essa rastreabilidade garante transparência e facilita análises de impacto.

---

# Evolução

Os cálculos poderão evoluir ao longo das versões do produto.

Toda alteração deverá ser documentada antes da implementação, preservando o histórico das mudanças, a compatibilidade dos indicadores existentes e a rastreabilidade institucional definida pela Deja Platform.