# Visualizações

## Objetivo

Este documento estabelece as diretrizes institucionais para apresentação dos indicadores da Deja Indicadores.

Seu objetivo é definir critérios para seleção das visualizações mais adequadas a cada indicador, promovendo clareza, consistência e melhor apoio à tomada de decisão.

As recomendações aqui descritas orientam a documentação dos indicadores, permanecendo independentes da tecnologia utilizada para construção da interface.

---

# Princípios

Toda visualização deverá:

- representar corretamente os dados;
- facilitar a interpretação dos resultados;
- evitar ambiguidades;
- preservar a consistência visual do produto;
- destacar informações relevantes;
- ser adequada ao objetivo analítico do indicador;
- manter acessibilidade e legibilidade.

A escolha da visualização deve priorizar a compreensão da informação, e não aspectos estéticos.

---

# Associação entre Indicadores e Visualizações

Cada indicador deverá informar explicitamente quais visualizações são recomendadas.

Uma mesma métrica poderá possuir múltiplas formas de apresentação, dependendo do contexto de utilização.

Exemplo:

```text
Indicador:
Faturamento Mensal

Visualizações recomendadas:

- Cartão de KPI
- Gráfico de Linhas
- Gráfico de Barras
- Série Temporal
```

---

# Tipos de Visualização

O catálogo poderá utilizar, entre outras, as seguintes formas de apresentação:

- cartão de KPI;
- tabela;
- tabela dinâmica;
- gráfico de barras;
- gráfico de colunas;
- gráfico de linhas;
- gráfico de áreas;
- gráfico de pizza;
- gráfico de rosca;
- gráfico de dispersão;
- histograma;
- mapa de calor;
- velocímetro;
- ranking;
- série temporal;
- indicadores comparativos;
- mapas geográficos.

Novos tipos poderão ser incorporados conforme a evolução do produto.

---

# Critérios de Escolha

A seleção da visualização deverá considerar:

- natureza do indicador;
- quantidade de informações apresentadas;
- necessidade de comparação;
- análise temporal;
- distribuição dos valores;
- identificação de tendências;
- perfil do usuário.

Nem toda visualização é adequada para qualquer indicador.

---

# Elementos Complementares

Sempre que aplicável, as visualizações poderão incluir:

- metas;
- linhas de referência;
- limites superiores e inferiores;
- indicadores de tendência;
- comparação com períodos anteriores;
- variação percentual;
- cores de status;
- legendas;
- descrições auxiliares.

Esses elementos ampliam o valor analítico da informação apresentada.

---

# Interação

Quando suportado pela interface do produto, as visualizações poderão oferecer recursos como:

- filtros;
- seleção de períodos;
- detalhamento (drill-down);
- agrupamentos;
- ordenação;
- comparação entre cenários;
- exportação de dados;
- navegação entre níveis analíticos.

A disponibilidade desses recursos dependerá da funcionalidade implementada.

---

# Consistência Visual

Para garantir uniformidade entre diferentes módulos da Deja Indicadores, deverão ser observados princípios como:

- padronização de nomenclaturas;
- utilização consistente de unidades de medida;
- escalas apropriadas;
- legendas padronizadas;
- representação uniforme de cores e estados;
- comportamento consistente entre dashboards.

Esses critérios contribuem para uma experiência analítica previsível e de fácil compreensão.

---

# Acessibilidade

As visualizações deverão considerar requisitos mínimos de acessibilidade, incluindo:

- contraste adequado;
- identificação por texto além das cores;
- suporte à navegação por teclado, quando aplicável;
- compatibilidade com tecnologias assistivas;
- legibilidade em diferentes resoluções.

A acessibilidade deverá ser considerada desde a especificação dos indicadores.

---

# Rastreabilidade

Cada visualização deverá manter vínculo com:

- indicador correspondente;
- requisitos funcionais;
- especificações funcionais;
- componentes responsáveis pela renderização;
- testes de interface, quando existentes.

Essa rastreabilidade facilita a evolução das apresentações sem comprometer a consistência do produto.

---

# Evolução

As recomendações deste documento poderão ser ampliadas à medida que novas formas de análise e visualização forem incorporadas à Deja Indicadores.

A evolução deverá preservar a padronização institucional, a consistência entre indicadores e a compatibilidade com a arquitetura do produto.