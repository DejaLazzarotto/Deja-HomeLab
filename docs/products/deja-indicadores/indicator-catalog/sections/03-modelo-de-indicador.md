# Modelo de Indicador

## Objetivo

Este documento define o modelo institucional utilizado para documentar cada indicador da Deja Indicadores.

Seu objetivo é garantir que todos os indicadores sejam especificados de forma uniforme, completa e rastreável, independentemente de sua complexidade ou domínio de negócio.

---

# Princípios

Todo indicador deverá ser documentado utilizando a mesma estrutura, permitindo:

- padronização da documentação;
- consistência entre implementações;
- facilidade de manutenção;
- rastreabilidade funcional e técnica;
- reutilização de componentes;
- automação futura da documentação.

---

# Estrutura Mínima

Cada indicador deverá conter, no mínimo, as seguintes informações:

- identificação;
- nome;
- objetivo;
- descrição funcional;
- contexto de negócio;
- categoria;
- fórmula de cálculo;
- parâmetros;
- dimensões analíticas;
- filtros suportados;
- origem dos dados;
- periodicidade;
- visualizações suportadas;
- limitações;
- rastreabilidade;
- requisitos de implementação;
- requisitos de testes;
- histórico de alterações.

Nenhum indicador poderá ser publicado sem o preenchimento desses elementos.

---

# Identificação

Todo indicador deverá possuir um identificador institucional único.

Exemplo:

```text
IND-001
IND-002
IND-003
```

O identificador é permanente e não deverá ser alterado ao longo do ciclo de vida do indicador.

---

# Informações Gerais

A documentação deverá registrar as informações básicas do indicador, incluindo:

- nome oficial;
- descrição resumida;
- objetivo de negócio;
- área funcional;
- versão;
- status;
- responsável pela manutenção.

Essas informações permitem a correta identificação e governança do indicador.

---

# Especificação Funcional

A especificação funcional deverá responder às seguintes questões:

- Qual problema o indicador resolve?
- Qual decisão ele apoia?
- Em quais cenários deve ser utilizado?
- Quais regras de negócio influenciam seu resultado?
- Quais limitações devem ser observadas?

Essa descrição deve utilizar linguagem de negócio, evitando detalhes de implementação.

---

# Especificação Técnica

A documentação técnica deverá definir claramente:

- fórmula de cálculo;
- variáveis envolvidas;
- regras de agregação;
- tratamento de valores nulos;
- tratamento de inconsistências;
- arredondamentos;
- unidades de medida;
- precisão numérica.

Essas definições asseguram que diferentes implementações produzam resultados equivalentes.

---

# Dados de Origem

Cada indicador deverá informar explicitamente:

- entidades envolvidas;
- atributos utilizados;
- fontes de dados;
- dependências;
- requisitos mínimos para cálculo;
- critérios de atualização.

A origem dos dados deve permanecer totalmente rastreável.

---

# Visualização

A documentação deverá indicar as formas recomendadas de apresentação do indicador.

Exemplos:

- cartão de KPI;
- tabela;
- gráfico de barras;
- gráfico de linhas;
- gráfico de pizza;
- série temporal;
- ranking;
- mapa;
- velocímetro;
- indicadores comparativos.

A especificação não impõe restrições à interface, mas orienta as visualizações mais adequadas.

---

# Implementação

Cada indicador deverá conter requisitos mínimos para implementação, incluindo:

- dependências funcionais;
- requisitos técnicos;
- serviços necessários;
- APIs utilizadas;
- regras de desempenho;
- requisitos de segurança;
- critérios de validação.

Essa seção estabelece o vínculo entre a documentação funcional e o desenvolvimento do produto.

---

# Testes

Todo indicador deverá possuir critérios objetivos para validação.

Os testes deverão contemplar, sempre que aplicável:

- cálculos corretos;
- tratamento de dados inválidos;
- ausência de dados;
- limites superiores e inferiores;
- desempenho;
- consistência entre períodos;
- consistência entre diferentes filtros.

---

# Rastreabilidade

Cada indicador deverá manter vínculo explícito com:

- Capability (CAP);
- Epic (EP);
- Functional Module (FM);
- Feature (FE);
- Functional Flow (FF);
- Functional Specification (FS);
- Arquitetura Técnica;
- Arquitetura de Implementação;
- código-fonte;
- testes automatizados.

Essa rastreabilidade garante total transparência sobre a origem e a evolução do indicador.

---

# Evolução

O modelo definido neste documento constitui o padrão oficial para documentação dos indicadores da Deja Indicadores.

Novos campos poderão ser incorporados futuramente, desde que preservem compatibilidade com a estrutura institucional e mantenham a padronização estabelecida para todo o catálogo.