# 06. Regras e Avaliação

## Objetivo

Este documento define o modelo institucional de regras diagnósticas e o processo de avaliação utilizado pelo Diagnostic Engine da Deja Indicadores.

Seu objetivo é garantir que todos os diagnósticos sejam produzidos de forma consistente, reproduzível, explicável e rastreável, independentemente da tecnologia utilizada em sua implementação.

---

# 1. Conceitos Fundamentais

O processo diagnóstico baseia-se na aplicação de regras estruturadas sobre um conjunto de evidências obtidas a partir de indicadores, contexto organizacional e conhecimento institucional.

Uma avaliação nunca depende de uma única condição isolada.

O diagnóstico é resultado da combinação de:

* contexto;
* evidências;
* regras;
* conhecimento institucional;
* critérios de classificação.

---

# 2. Regra Diagnóstica

Uma regra diagnóstica representa uma condição formal utilizada para interpretar uma situação organizacional.

Cada regra possui identidade própria e pode ser reutilizada por diferentes definições diagnósticas.

Uma regra deve possuir, no mínimo:

* identificador;
* nome;
* objetivo;
* descrição;
* expressão lógica;
* parâmetros;
* prioridade;
* severidade associada;
* estado do ciclo de vida;
* versão.

---

# 3. Tipos de Regras

O Diagnostic Engine pode trabalhar com diferentes categorias de regras.

## Regras de Limite

Verificam se um indicador encontra-se acima ou abaixo de valores de referência.

Exemplos:

* faturamento abaixo da meta;
* estoque acima do limite;
* inadimplência superior ao máximo permitido.

---

## Regras de Tendência

Avaliam a evolução temporal de indicadores.

Exemplos:

* crescimento contínuo;
* queda persistente;
* aceleração;
* desaceleração.

---

## Regras Comparativas

Comparam indicadores entre períodos, unidades ou grupos.

Exemplos:

* filial A versus filial B;
* mês atual versus mesmo mês do ano anterior;
* centro de custo versus média corporativa.

---

## Regras de Correlação

Relacionam múltiplos indicadores simultaneamente.

Exemplos:

* aumento de vendas sem aumento proporcional da margem;
* crescimento do faturamento acompanhado por aumento da inadimplência.

---

## Regras Contextuais

Consideram características específicas do ambiente avaliado.

Exemplos:

* sazonalidade;
* segmento de mercado;
* porte da empresa;
* regime tributário;
* localização geográfica.

---

## Regras Baseadas em Conhecimento

Utilizam conceitos, metodologias e interpretações registrados na Knowledge Base.

Essas regras permitem incorporar conhecimento institucional ao processo diagnóstico.

---

# 4. Evidências

As regras operam exclusivamente sobre evidências estruturadas.

As evidências podem ser provenientes de:

* indicadores;
* métricas derivadas;
* eventos;
* atributos organizacionais;
* informações históricas;
* parâmetros externos;
* itens da Knowledge Base.

Cada evidência deve manter vínculo com sua origem.

---

# 5. Processo de Avaliação

O processo institucional de avaliação segue as etapas abaixo.

```text id="4gtyrz"
Contexto
      │
      ▼
Coleta de Evidências
      │
      ▼
Validação
      │
      ▼
Execução das Regras
      │
      ▼
Consolidação
      │
      ▼
Classificação
      │
      ▼
Confiança
      │
      ▼
Explicação
      │
      ▼
Instância de Diagnóstico
```

Cada etapa produz informações utilizadas pelas etapas seguintes.

---

# 6. Consolidação

Durante a avaliação, diferentes regras podem produzir resultados parciais.

O processo de consolidação é responsável por:

* combinar resultados;
* eliminar redundâncias;
* resolver conflitos;
* priorizar evidências;
* produzir uma conclusão única.

Essa consolidação permanece documentada para fins de auditoria.

---

# 7. Classificação

Após a consolidação, o diagnóstico recebe classificações institucionais.

Entre elas:

* natureza;
* severidade;
* impacto;
* prioridade;
* domínio;
* criticidade.

A classificação facilita o consumo dos diagnósticos pelos demais componentes da plataforma.

---

# 8. Nível de Confiança

Todo diagnóstico recebe um nível de confiança calculado a partir de critérios institucionais.

Podem influenciar esse cálculo:

* completude dos dados;
* qualidade das evidências;
* convergência das regras;
* quantidade de evidências disponíveis;
* consistência das informações.

A confiança representa o grau de robustez da conclusão obtida.

---

# 9. Explicabilidade

Todo diagnóstico deve ser acompanhado por uma explicação estruturada.

Essa explicação deve responder, no mínimo:

* quais evidências foram utilizadas;
* quais regras foram executadas;
* quais condições foram satisfeitas;
* quais condições foram rejeitadas;
* qual conhecimento fundamentou a conclusão;
* por que o diagnóstico foi emitido.

A explicabilidade é requisito obrigatório da arquitetura institucional.

---

# 10. Reprodutibilidade

Uma mesma definição diagnóstica, executada sobre o mesmo conjunto de evidências e no mesmo contexto, deve produzir o mesmo resultado.

Esse princípio garante:

* consistência;
* previsibilidade;
* auditoria;
* governança;
* confiabilidade.

---

# 11. Tratamento de Exceções

Durante a avaliação podem ocorrer situações excepcionais, como:

* ausência de indicadores;
* dados incompletos;
* inconsistências nas evidências;
* regras incompatíveis;
* parâmetros inválidos;
* contexto insuficiente.

Essas situações devem ser registradas e incorporadas ao histórico da avaliação, preservando a rastreabilidade do processo.

---

# 12. Evolução das Regras

As regras diagnósticas evoluem continuamente.

Cada alteração deve preservar:

* histórico;
* versão;
* documentação;
* rastreabilidade;
* compatibilidade institucional.

Diagnósticos já emitidos permanecem vinculados à versão vigente no momento de sua execução.

---

# Síntese

O modelo de regras e avaliação estabelece a base institucional para produção de diagnósticos consistentes na Deja Indicadores.

Ao estruturar regras reutilizáveis, evidências rastreáveis, avaliações reproduzíveis, classificações padronizadas e explicações auditáveis, o Diagnostic Engine torna-se capaz de interpretar indicadores de forma confiável, transparente e alinhada aos princípios de governança definidos para o Núcleo de Inteligência.
