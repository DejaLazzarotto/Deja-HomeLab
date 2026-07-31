# 08. Rastreabilidade

## Objetivo

Esta seção estabelece o modelo institucional de rastreabilidade do Decision Engine.

Toda decisão produzida deverá manter vínculos explícitos com os ativos utilizados durante o processo decisório, permitindo auditoria, transparência e reprodutibilidade.

A rastreabilidade constitui um dos pilares da governança da Deja Indicadores.

---

## Princípios

A rastreabilidade deve garantir:

- identificação da origem das informações;
- reconstrução completa do processo decisório;
- transparência da justificativa;
- auditoria integral;
- versionamento dos ativos utilizados;
- preservação do histórico.

Nenhuma decisão institucional deverá existir sem rastreabilidade.

---

## Cadeia de rastreabilidade

Cada Decision Instance deverá manter vínculos com toda a cadeia de inteligência.

```text
Knowledge Item
        │
        ▼
Indicator
        │
        ▼
Diagnostic Instance
        │
        ▼
Recommendation Instance
        │
        ▼
Decision Instance
```

Essa cadeia representa a origem de todas as evidências utilizadas durante a consolidação da decisão.

---

## Ativos rastreados

Uma decisão poderá manter referências para:

- Knowledge Items;
- Indicators;
- Diagnostic Definitions;
- Diagnostic Instances;
- Recommendation Definitions;
- Recommendation Instances;
- Decision Definition;
- Decision Policies;
- Decision Rules;
- Decision Criteria;
- Decision Constraints.

Todos esses ativos deverão possuir identificadores institucionais únicos.

---

## Informações rastreadas

Além das referências aos ativos, a Decision Instance deverá preservar:

- contexto utilizado;
- alternativas avaliadas;
- alternativa selecionada;
- justificativa;
- critérios aplicados;
- políticas consideradas;
- restrições avaliadas;
- prioridade;
- nível de confiança;
- resultado produzido.

Essas informações permitem compreender integralmente o processo decisório.

---

## Versionamento

A rastreabilidade deverá registrar a versão de cada ativo utilizado durante a decisão.

Entre eles:

- versão do indicador;
- versão do diagnóstico;
- versão da recomendação;
- versão das políticas;
- versão das regras;
- versão dos critérios;
- versão das restrições;
- versão da Decision Definition.

Esse mecanismo assegura a reprodutibilidade histórica das decisões.

---

## Auditoria

A rastreabilidade deve permitir responder, entre outras, às seguintes questões:

- Quais diagnósticos originaram esta decisão?
- Quais recomendações foram avaliadas?
- Quais alternativas foram descartadas?
- Quais políticas influenciaram a decisão?
- Quais critérios determinaram a escolha?
- Quais restrições eliminaram alternativas?
- Qual justificativa foi registrada?
- Qual era o nível de confiança da decisão?
- Quais versões dos ativos estavam vigentes?

Essas informações constituem a base da auditoria institucional.

---

## Reprodutibilidade

Uma decisão deverá poder ser reproduzida sempre que o mesmo conjunto de informações estiver disponível.

A reprodutibilidade depende da preservação de:

- contexto;
- ativos utilizados;
- versões;
- políticas;
- critérios;
- restrições;
- regras aplicadas.

Esse princípio garante consistência e previsibilidade do processo decisório.

---

## Integração com a governança

O modelo de rastreabilidade integra-se diretamente aos mecanismos de governança da Deja Indicadores.

Os registros produzidos pelo Decision Engine apoiam:

- auditorias internas;
- auditorias externas;
- conformidade regulatória;
- revisão de decisões;
- melhoria contínua;
- evolução das políticas institucionais.

---

## Papel institucional

A rastreabilidade transforma cada Decision Instance em um registro corporativo verificável e auditável.

Dessa forma, o Decision Engine preserva a transparência do processo decisório, fortalece a governança organizacional e assegura que todas as decisões produzidas pela Deja Indicadores possam ser compreendidas, justificadas e reproduzidas ao longo do tempo.