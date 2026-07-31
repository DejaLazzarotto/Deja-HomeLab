# 05. Componentes

## Objetivo

Este documento descreve os componentes institucionais que compõem o Diagnostic Engine da Deja Indicadores.

Cada componente possui uma responsabilidade única e bem definida, favorecendo baixo acoplamento, reutilização, governança e evolução independente.

---

# 1. Visão Geral

O Diagnostic Engine é organizado como um conjunto de componentes especializados que cooperam durante a execução de um diagnóstico.

A arquitetura evita componentes monolíticos, distribuindo responsabilidades entre módulos coesos e independentes.

O fluxo geral pode ser representado por:

```text
Diagnostic Definition Registry
                │
                ▼
Diagnostic Context Resolver
                │
                ▼
Diagnostic Evidence Resolver
                │
                ▼
Diagnostic Rule Engine
                │
                ▼
Diagnostic Evaluation Engine
                │
                ▼
Diagnostic Classification Engine
                │
                ▼
Diagnostic Confidence Evaluator
                │
                ▼
Diagnostic Explanation Builder
                │
                ▼
Diagnostic Trace Registry
                │
                ▼
Diagnostic Result Repository
```

---

# 2. Diagnostic Definition Registry

É o repositório institucional das definições diagnósticas.

Responsabilidades:

* registrar definições;
* localizar diagnósticos;
* controlar versões;
* controlar estados do ciclo de vida;
* disponibilizar definições para avaliação.

Não executa regras nem produz diagnósticos.

---

# 3. Diagnostic Context Resolver

Responsável por construir o contexto da avaliação.

Entre suas funções:

* identificar organização;
* identificar unidade;
* determinar período;
* resolver parâmetros;
* validar escopo da execução.

O contexto produzido será utilizado por todos os demais componentes.

---

# 4. Diagnostic Evidence Resolver

Localiza e organiza todas as evidências necessárias para a avaliação.

Pode consultar:

* Indicator Catalog;
* Knowledge Base;
* eventos;
* atributos organizacionais;
* parâmetros externos;
* históricos.

Seu resultado é um conjunto estruturado de evidências.

---

# 5. Diagnostic Rule Engine

Executa as regras diagnósticas definidas para cada diagnóstico.

Responsabilidades:

* interpretar regras;
* avaliar condições;
* combinar evidências;
* registrar resultados intermediários;
* produzir conclusões parciais.

As regras permanecem independentes da implementação técnica.

---

# 6. Diagnostic Evaluation Engine

Coordena toda a execução do processo diagnóstico.

Entre suas responsabilidades:

* iniciar avaliação;
* controlar fluxo;
* executar regras;
* consolidar resultados;
* gerar a instância diagnóstica.

Este componente representa o núcleo operacional do Diagnostic Engine.

---

# 7. Diagnostic Classification Engine

Classifica o diagnóstico produzido.

Pode atribuir classificações relacionadas a:

* natureza;
* severidade;
* impacto;
* prioridade;
* domínio;
* criticidade.

As classificações seguem padrões institucionais definidos pela plataforma.

---

# 8. Diagnostic Confidence Evaluator

Calcula o nível de confiança do diagnóstico.

Pode considerar:

* quantidade de evidências;
* qualidade dos dados;
* convergência das informações;
* cobertura das regras;
* consistência dos resultados.

O nível de confiança complementa o diagnóstico sem alterar sua conclusão.

---

# 9. Diagnostic Explanation Builder

Produz a explicação estruturada do diagnóstico.

A explicação deve registrar:

* evidências utilizadas;
* regras executadas;
* fundamentos;
* justificativas;
* referências ao conhecimento;
* fatores relevantes para a conclusão.

Esse componente garante transparência ao processo decisório.

---

# 10. Diagnostic Trace Registry

Mantém a rastreabilidade completa da avaliação.

Entre as informações registradas estão:

* definição utilizada;
* versão;
* contexto;
* evidências;
* regras;
* classificações;
* explicações;
* horário da execução;
* resultado final.

O histórico produzido permite auditoria completa do processo.

---

# 11. Diagnostic Result Repository

Armazena as instâncias diagnósticas produzidas.

Cada instância preserva:

* identidade;
* versão;
* contexto;
* explicação;
* classificação;
* rastreabilidade;
* confiança;
* referências utilizadas.

Os resultados permanecem disponíveis para consultas futuras e integração com outros componentes.

---

# 12. Integração entre Componentes

Os componentes cooperam por meio de contratos institucionais.

Nenhum componente depende diretamente da implementação interna dos demais.

Essa organização favorece:

* substituição de implementações;
* evolução incremental;
* testes independentes;
* reutilização;
* escalabilidade.

---

# 13. Integração Externa

O Diagnostic Engine comunica-se principalmente com:

### Indicator Catalog

Fornecedor oficial dos indicadores e metadados.

### Knowledge Base

Fornecedor oficial do conhecimento institucional.

### Recommendation Engine

Consumidor oficial dos diagnósticos produzidos.

### AI Assistant

Consumidor das explicações, classificações, evidências e resultados diagnósticos.

Cada integração ocorre por contratos bem definidos, preservando baixo acoplamento.

---

# 14. Evolução Arquitetural

Novos componentes poderão ser adicionados futuramente, como:

* Detection Engine;
* Pattern Recognition Engine;
* Root Cause Analyzer;
* Scenario Simulator;
* Predictive Diagnosis;
* Explainability Enhancer.

Essas evoluções deverão respeitar os contratos públicos existentes, garantindo compatibilidade com as versões anteriores.

---

# Síntese

A arquitetura do Diagnostic Engine é composta por componentes especializados e independentes, cada um responsável por uma etapa específica do processo diagnóstico.

Essa organização assegura modularidade, reutilização, rastreabilidade e governança, formando a base para um motor de diagnósticos gerenciais robusto, extensível e alinhado aos princípios arquiteturais da Deja Indicadores.
