# Diagnostic Engine — Deja Indicadores

O **Diagnostic Engine** é o componente institucional do Núcleo de Inteligência da Deja Indicadores responsável por transformar indicadores, dados, regras e conhecimento corporativo em diagnósticos gerenciais estruturados, rastreáveis e reutilizáveis.

Seu objetivo é identificar situações relevantes para o negócio, interpretar evidências, classificar condições organizacionais e produzir conclusões diagnósticas que possam orientar decisões, recomendações e interações inteligentes.

O Diagnostic Engine atua de forma independente das tecnologias de persistência, visualização, inteligência artificial ou interface com o usuário.

---

## 1. Papel institucional

O Diagnostic Engine estabelece a arquitetura oficial para geração de diagnósticos na Deja Indicadores.

Ele é responsável por:

* receber indicadores e evidências organizacionais;
* avaliar condições e regras diagnósticas;
* consultar conhecimento institucional;
* identificar situações gerenciais relevantes;
* gerar diagnósticos estruturados;
* classificar severidade, impacto, prioridade e confiança;
* registrar as evidências utilizadas;
* preservar a rastreabilidade das conclusões;
* disponibilizar diagnósticos para outros componentes da plataforma.

O Diagnostic Engine não substitui o Indicator Catalog nem a Knowledge Base.

Cada componente possui responsabilidade própria:

* o **Indicator Catalog** define os indicadores e seus cálculos;
* a **Knowledge Base** mantém o conhecimento institucional reutilizável;
* o **Diagnostic Engine** interpreta indicadores e evidências;
* o **Recommendation Engine** transforma diagnósticos em ações recomendadas;
* o **AI Assistant** utiliza esses ativos para interação e apoio inteligente ao usuário.

---

## 2. Princípios fundamentais

O Diagnostic Engine adota os seguintes princípios institucionais:

* diagnósticos devem ser estruturados e identificáveis;
* toda conclusão deve possuir evidências rastreáveis;
* regras diagnósticas devem ser explícitas e governáveis;
* diagnósticos devem permanecer independentes de interfaces;
* conhecimento e lógica diagnóstica devem ser reutilizáveis;
* indicadores não devem conter regras diagnósticas específicas;
* recomendações não devem ser produzidas diretamente pelo diagnóstico;
* a inteligência artificial não deve ser a única responsável pela conclusão;
* diagnósticos devem possuir versionamento;
* resultados devem ser explicáveis e auditáveis;
* diferentes contextos podem produzir interpretações distintas para a mesma evidência;
* a evolução das regras não deve invalidar o histórico de diagnósticos já emitidos.

---

## 3. Unidade institucional de diagnóstico

A menor unidade institucional do Diagnostic Engine é o **Diagnostic Definition**.

Uma definição de diagnóstico representa uma situação organizacional que pode ser identificada por meio da avaliação de evidências, indicadores, regras e conhecimento corporativo.

Cada definição possui, no mínimo:

* identificador institucional;
* nome;
* descrição;
* objetivo;
* contexto de aplicação;
* condições de avaliação;
* evidências necessárias;
* regras diagnósticas;
* classificação;
* severidade;
* impacto esperado;
* referências ao conhecimento;
* referências aos indicadores;
* versão;
* estado do ciclo de vida;
* responsáveis;
* histórico de alterações.

A execução de uma definição de diagnóstico produz uma **Diagnostic Instance**.

A instância representa o resultado concreto de uma avaliação realizada para uma organização, unidade, período ou contexto específico.

---

## 4. Modelo conceitual

O modelo institucional do Diagnostic Engine é composto pelos seguintes elementos:

* **Diagnostic Definition**
  Define formalmente uma situação que pode ser diagnosticada.

* **Diagnostic Rule**
  Representa uma condição lógica utilizada durante a avaliação.

* **Diagnostic Evidence**
  Representa um dado, indicador, evento, conhecimento ou informação utilizada como evidência.

* **Diagnostic Context**
  Define o escopo organizacional, temporal e operacional da avaliação.

* **Diagnostic Evaluation**
  Representa o processo de aplicação das regras sobre as evidências.

* **Diagnostic Instance**
  Representa o diagnóstico produzido após a avaliação.

* **Diagnostic Classification**
  Classifica o diagnóstico por natureza, domínio, severidade, impacto ou prioridade.

* **Diagnostic Explanation**
  Registra de forma compreensível como a conclusão foi obtida.

* **Diagnostic Confidence**
  Representa o nível de confiança atribuído ao resultado.

* **Diagnostic Trace**
  Preserva a rastreabilidade completa da avaliação.

---

## 5. Componentes institucionais

A arquitetura do Diagnostic Engine é organizada nos seguintes componentes:

### 5.1 Diagnostic Definition Registry

Responsável pelo registro, consulta e versionamento das definições de diagnóstico.

### 5.2 Diagnostic Rule Engine

Responsável pela avaliação das regras diagnósticas sobre as evidências disponíveis.

### 5.3 Diagnostic Evidence Resolver

Responsável por localizar, validar e preparar as evidências necessárias para uma avaliação.

### 5.4 Diagnostic Context Resolver

Responsável por determinar o contexto organizacional e temporal da execução.

### 5.5 Diagnostic Evaluation Engine

Responsável por coordenar a execução completa de uma avaliação diagnóstica.

### 5.6 Diagnostic Classification Engine

Responsável por classificar os resultados conforme severidade, impacto, prioridade, domínio e natureza.

### 5.7 Diagnostic Explanation Builder

Responsável por construir explicações estruturadas e compreensíveis sobre os resultados.

### 5.8 Diagnostic Confidence Evaluator

Responsável por determinar o nível de confiança da conclusão produzida.

### 5.9 Diagnostic Trace Registry

Responsável por registrar a origem das evidências, regras executadas, decisões intermediárias e resultado final.

### 5.10 Diagnostic Result Repository

Responsável pela persistência e recuperação das instâncias de diagnóstico produzidas.

---

## 6. Integrações institucionais

O Diagnostic Engine integra-se aos demais componentes da Deja Indicadores.

### Indicator Catalog

Fornece:

* definições de indicadores;
* valores calculados;
* metadados;
* períodos de referência;
* fontes de dados;
* histórico;
* qualidade e confiabilidade dos dados.

### Knowledge Base

Fornece:

* conceitos;
* definições;
* metodologias;
* referências;
* interpretações;
* critérios;
* padrões organizacionais;
* conhecimento contextual.

### Recommendation Engine

Recebe:

* diagnósticos válidos;
* severidade;
* impacto;
* prioridade;
* evidências;
* contexto;
* explicações;
* nível de confiança.

O Recommendation Engine permanece responsável por produzir ações recomendadas.

### AI Assistant

Utiliza os diagnósticos para:

* explicar situações ao usuário;
* responder perguntas;
* contextualizar resultados;
* comparar períodos;
* explorar causas;
* apresentar evidências;
* apoiar processos decisórios.

O AI Assistant não substitui o mecanismo institucional de avaliação do Diagnostic Engine.

---

## 7. Rastreabilidade

Toda instância de diagnóstico deve preservar a cadeia completa de rastreabilidade:

```text
Organização
    ↓
Contexto
    ↓
Fonte de Dados
    ↓
Indicador
    ↓
Evidência
    ↓
Regra Diagnóstica
    ↓
Definição de Diagnóstico
    ↓
Avaliação
    ↓
Instância de Diagnóstico
    ↓
Recomendação
    ↓
Interação com o Usuário
```

A rastreabilidade deve permitir responder:

* quais dados foram utilizados;
* quais indicadores participaram;
* quais regras foram executadas;
* quais condições foram satisfeitas;
* quais condições não foram satisfeitas;
* qual versão da definição foi utilizada;
* qual conhecimento fundamentou a interpretação;
* como a severidade foi determinada;
* como o nível de confiança foi calculado;
* quando o diagnóstico foi produzido;
* para qual contexto o diagnóstico é válido.

---

## 8. Governança

Toda definição de diagnóstico deve possuir:

* responsável institucional;
* responsável técnico;
* versão;
* estado do ciclo de vida;
* data de criação;
* data de revisão;
* critérios de validade;
* referências documentais;
* histórico de alterações;
* vínculos com indicadores;
* vínculos com itens de conhecimento;
* política de revisão.

Os estados institucionais recomendados são:

* `draft`;
* `review`;
* `approved`;
* `active`;
* `deprecated`;
* `archived`.

Somente definições aprovadas e ativas podem ser utilizadas em avaliações oficiais.

---

## 9. Organização documental

A documentação oficial do Diagnostic Engine está organizada da seguinte forma:

```text
diagnostic-engine/
├── README.md
├── diagnostic-engine-v1.md
└── sections/
    ├── 01-visao-geral.md
    ├── 02-principios.md
    ├── 03-organizacao.md
    ├── 04-modelo-de-diagnostico.md
    ├── 05-componentes.md
    ├── 06-regras-e-avaliacao.md
    ├── 07-integracao.md
    ├── 08-rastreabilidade.md
    ├── 09-governanca.md
    └── 10-evolucao.md
```

O arquivo `diagnostic-engine-v1.md` constitui o Documento Mestre da arquitetura documental do Diagnostic Engine.

Os documentos localizados em `sections/` detalham individualmente cada dimensão institucional da arquitetura.

---

## 10. Independência arquitetural

O Diagnostic Engine deve permanecer independente:

* da tecnologia de banco de dados;
* do mecanismo de mensageria;
* da interface gráfica;
* do framework frontend;
* da tecnologia de backend;
* do provedor de inteligência artificial;
* da ferramenta de Business Intelligence;
* do formato físico das fontes de dados;
* do mecanismo de visualização;
* do canal comercial utilizado pelo produto.

Essa independência permite que o motor de diagnóstico evolua sem comprometer os demais componentes da plataforma.

---

## 11. Evolução

A evolução do Diagnostic Engine deve ocorrer de forma incremental e governada.

As primeiras versões devem priorizar:

1. definições diagnósticas explícitas;
2. regras determinísticas;
3. evidências baseadas em indicadores;
4. classificação por severidade;
5. explicações rastreáveis;
6. armazenamento das instâncias produzidas;
7. integração com o Recommendation Engine;
8. integração assistida com inteligência artificial.

Recursos probabilísticos, aprendizado de máquina e modelos generativos devem complementar a arquitetura institucional, nunca substituir sua rastreabilidade, governança e explicabilidade.

---

## 12. Documento Mestre

A especificação completa do Diagnostic Engine está consolidada em:

`diagnostic-engine-v1.md`

Esse documento estabelece a visão integrada da arquitetura e referencia todas as seções especializadas.
