# 06. Geração de Recomendações

## Objetivo

Este documento descreve o processo institucional utilizado pelo Recommendation Engine para produzir recomendações gerenciais a partir dos diagnósticos gerados pelo Diagnostic Engine.

O processo estabelece uma sequência estruturada de etapas responsáveis por selecionar, priorizar, justificar e registrar recomendações de forma consistente, rastreável e reutilizável.

---

# 1. Visão Geral

A geração de recomendações constitui o fluxo operacional central do Recommendation Engine.

Seu objetivo é transformar evidências já interpretadas pelo Diagnostic Engine em orientações práticas para apoio à tomada de decisão.

O processo não altera diagnósticos nem executa ações operacionais.

Seu resultado é a produção de Recommendation Instances.

---

# 2. Entradas do Processo

O processo pode utilizar, entre outras, as seguintes informações:

* diagnósticos;
* severidade;
* impacto;
* prioridade;
* contexto organizacional;
* regras de recomendação;
* políticas corporativas;
* conhecimento institucional;
* parâmetros de execução.

Essas entradas são tratadas de forma independente da tecnologia de origem.

---

# 3. Fluxo Institucional

O fluxo institucional pode ser representado da seguinte forma:

```text id="0grn7t"
Diagnóstico
      │
      ▼
Resolução do Contexto
      │
      ▼
Seleção das Recommendation Definitions
      │
      ▼
Execução das Recommendation Rules
      │
      ▼
Avaliação de Elegibilidade
      │
      ▼
Priorização
      │
      ▼
Construção da Justificativa
      │
      ▼
Registro da Rastreabilidade
      │
      ▼
Recommendation Instance
```

Cada etapa produz informações utilizadas pelas etapas subsequentes.

---

# 4. Resolução do Contexto

Antes da avaliação das regras, o Recommendation Engine constrói o contexto da execução.

Podem ser considerados:

* organização;
* unidade;
* período;
* domínio funcional;
* políticas corporativas;
* prioridades estratégicas;
* restrições operacionais.

O contexto influencia diretamente a elegibilidade e a priorização das recomendações.

---

# 5. Seleção das Recommendation Definitions

Com o contexto definido, o Recommendation Definition Registry identifica as definições potencialmente aplicáveis.

A seleção considera:

* domínio;
* escopo;
* estado do ciclo de vida;
* versão ativa;
* compatibilidade com o diagnóstico;
* restrições institucionais.

Somente definições elegíveis seguem para avaliação.

---

# 6. Execução das Recommendation Rules

Para cada definição selecionada, o Recommendation Rule Engine executa suas regras institucionais.

Durante essa etapa podem ser avaliados:

* características do diagnóstico;
* indicadores relacionados;
* contexto;
* políticas organizacionais;
* conhecimento institucional;
* dependências entre recomendações.

O resultado é a determinação da elegibilidade de cada definição.

---

# 7. Avaliação de Elegibilidade

A Recommendation Evaluation consolida os resultados das regras executadas.

Cada Recommendation Definition poderá ser classificada como:

* elegível;
* não elegível;
* parcialmente elegível;
* bloqueada por restrições.

Essa classificação orienta a próxima etapa do processo.

---

# 8. Priorização

As recomendações elegíveis são ordenadas segundo critérios institucionais.

Entre os fatores considerados estão:

* severidade do diagnóstico;
* impacto esperado;
* urgência;
* risco;
* dependências;
* políticas organizacionais;
* contexto de negócio.

A priorização representa uma sugestão de ordem de atuação e não uma obrigação.

---

# 9. Construção da Justificativa

Para cada Recommendation Instance é construída uma justificativa estruturada.

A justificativa registra:

* diagnóstico de origem;
* Recommendation Definition utilizada;
* regras executadas;
* critérios considerados;
* referências da Knowledge Base;
* contexto avaliado;
* fundamentos da recomendação.

Essa justificativa garante transparência e explicabilidade.

---

# 10. Registro da Rastreabilidade

Após a geração da recomendação, o Recommendation Trace Registry registra toda a cadeia de execução.

São preservadas informações como:

* versão da Recommendation Definition;
* versão das regras;
* diagnóstico utilizado;
* contexto;
* justificativa;
* prioridade calculada;
* instante da execução.

Esses registros permitem auditoria completa do processo.

---

# 11. Resultado

O resultado final do processo é uma Recommendation Instance contendo, entre outros elementos:

* identificador;
* Recommendation Definition;
* diagnóstico relacionado;
* contexto;
* prioridade;
* justificativa;
* impacto esperado;
* referências institucionais;
* rastreabilidade completa.

Essa instância torna-se o artefato oficial disponibilizado aos demais componentes da plataforma.

---

# 12. Consumo das Recomendações

As Recommendation Instances podem ser consumidas por diferentes componentes da Deja Indicadores.

Entre eles:

* dashboards;
* relatórios;
* módulos funcionais;
* APIs;
* AI Assistant;
* integrações externas.

Todos os consumidores acessam as recomendações por meio de contratos institucionais, preservando baixo acoplamento e independência tecnológica.

---

# Síntese

O processo de geração de recomendações transforma diagnósticos em orientações estruturadas por meio de um fluxo institucional composto por resolução de contexto, seleção de definições, execução de regras, avaliação, priorização, justificativa e rastreabilidade.

Essa arquitetura garante que todas as recomendações produzidas pela Deja Indicadores sejam consistentes, justificáveis, auditáveis e reutilizáveis, mantendo a separação entre análise, recomendação e decisão.
