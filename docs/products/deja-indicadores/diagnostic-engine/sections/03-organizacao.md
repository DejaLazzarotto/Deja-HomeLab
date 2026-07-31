# 03. Organização

## Objetivo

Este documento define a organização institucional do Diagnostic Engine, estabelecendo como seus ativos são estruturados, identificados, versionados e relacionados entre si.

A organização proposta prioriza reutilização, governança, rastreabilidade e evolução incremental.

---

# 1. Organização Geral

O Diagnostic Engine é organizado em torno de definições diagnósticas independentes.

Cada definição representa uma situação organizacional que pode ser identificada por meio da avaliação estruturada de evidências.

O motor executa essas definições produzindo instâncias concretas de diagnóstico.

O conhecimento necessário para interpretar as evidências permanece na Knowledge Base, enquanto os indicadores permanecem definidos no Indicator Catalog.

---

# 2. Ativos Institucionais

Os principais ativos do Diagnostic Engine são:

* Diagnostic Definition;
* Diagnostic Rule;
* Diagnostic Evidence;
* Diagnostic Context;
* Diagnostic Evaluation;
* Diagnostic Instance;
* Diagnostic Classification;
* Diagnostic Explanation;
* Diagnostic Confidence;
* Diagnostic Trace.

Cada ativo possui finalidade específica e responsabilidade claramente definida.

---

# 3. Diagnostic Definition

A Diagnostic Definition representa a menor unidade institucional do Diagnostic Engine.

Cada definição identifica formalmente uma situação gerencial que pode ser diagnosticada.

Uma definição contém, entre outros elementos:

* identificador institucional;
* nome;
* objetivo;
* descrição;
* domínio;
* contexto aplicável;
* regras diagnósticas;
* evidências necessárias;
* classificações possíveis;
* versão;
* estado do ciclo de vida.

As definições são reutilizáveis entre organizações, períodos e contextos compatíveis.

---

# 4. Diagnostic Rule

As regras diagnósticas descrevem as condições utilizadas para avaliar uma situação.

Cada regra deve possuir:

* identificador;
* objetivo;
* expressão lógica;
* parâmetros;
* severidade associada;
* prioridade;
* documentação;
* histórico de alterações.

As regras permanecem independentes da implementação tecnológica.

---

# 5. Diagnostic Evidence

As evidências representam os elementos utilizados durante a avaliação.

Uma evidência pode originar-se de:

* indicadores;
* métricas;
* eventos;
* atributos organizacionais;
* parâmetros externos;
* informações históricas;
* itens da Knowledge Base.

Cada evidência mantém referência completa à sua origem.

---

# 6. Diagnostic Context

O contexto define o ambiente em que a avaliação ocorre.

Entre os elementos que podem compor um contexto estão:

* organização;
* unidade de negócio;
* período;
* filial;
* centro de custo;
* processo;
* área funcional;
* segmento;
* demais parâmetros institucionais.

O contexto influencia diretamente a interpretação das evidências.

---

# 7. Diagnostic Evaluation

A avaliação representa o processo institucional de aplicação das regras sobre o conjunto de evidências disponíveis.

Durante esse processo são registrados:

* evidências utilizadas;
* regras executadas;
* condições satisfeitas;
* condições rejeitadas;
* justificativas;
* classificações intermediárias;
* resultados finais.

A avaliação preserva todas as informações necessárias para auditoria futura.

---

# 8. Diagnostic Instance

A execução de uma definição diagnóstica produz uma Diagnostic Instance.

Cada instância representa um diagnóstico efetivamente realizado para um determinado contexto.

Ela contém:

* definição utilizada;
* versão da definição;
* contexto;
* evidências;
* classificação;
* severidade;
* impacto;
* confiança;
* explicação;
* data da avaliação;
* rastreabilidade completa.

As instâncias constituem registros permanentes da plataforma.

---

# 9. Organização das Relações

A relação entre os ativos pode ser representada da seguinte forma:

```text
Diagnostic Definition
          │
          ├────────► Diagnostic Rule
          │
          ├────────► Diagnostic Evidence
          │
          ├────────► Diagnostic Context
          │
          ▼
Diagnostic Evaluation
          │
          ▼
Diagnostic Instance
          │
          ├────────► Diagnostic Classification
          ├────────► Diagnostic Confidence
          ├────────► Diagnostic Explanation
          └────────► Diagnostic Trace
```

Esse modelo favorece reutilização, baixo acoplamento e evolução independente.

---

# 10. Organização por Domínio

As definições diagnósticas podem ser agrupadas por domínio funcional.

Exemplos:

* Financeiro;
* Comercial;
* Produção;
* Compras;
* Estoque;
* Logística;
* Recursos Humanos;
* Qualidade;
* Projetos;
* Sustentabilidade.

Essa organização facilita manutenção, governança e descoberta de ativos.

---

# 11. Organização por Ciclo de Vida

Toda definição diagnóstica percorre um ciclo institucional composto pelos estados:

* Draft;
* Review;
* Approved;
* Active;
* Deprecated;
* Archived.

Somente definições ativas podem ser utilizadas em avaliações oficiais.

---

# 12. Organização por Versionamento

Cada evolução significativa gera uma nova versão da definição diagnóstica.

O versionamento preserva:

* compatibilidade histórica;
* rastreabilidade;
* auditoria;
* reprodutibilidade das avaliações realizadas.

Instâncias já produzidas nunca alteram automaticamente sua versão de referência.

---

# 13. Organização Documental

A documentação institucional do Diagnostic Engine permanece organizada em:

```text
diagnostic-engine/
├── README.md
├── diagnostic-engine-v1.md
└── sections/
```

Cada documento aborda uma dimensão específica da arquitetura, mantendo separação entre conceitos, princípios, componentes, integração, governança e evolução.

---

# Síntese

A organização institucional do Diagnostic Engine estabelece uma estrutura modular baseada em ativos independentes, claramente identificados e versionados.

Essa organização garante reutilização das definições diagnósticas, preserva a rastreabilidade das avaliações e permite que o componente evolua continuamente sem comprometer a estabilidade da arquitetura da Deja Indicadores.
