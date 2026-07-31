# 02. Princípios

## Objetivo

Este documento estabelece os princípios arquiteturais que orientam o desenvolvimento, evolução e utilização do Diagnostic Engine da Deja Indicadores.

Esses princípios garantem que os diagnósticos produzidos permaneçam consistentes, explicáveis, rastreáveis e reutilizáveis, independentemente da tecnologia empregada em sua implementação.

---

# 1. Diagnóstico como ativo corporativo

Todo diagnóstico representa um ativo institucional da plataforma.

Ele não deve ser tratado como uma simples resposta transitória, mas como uma interpretação formal da realidade organizacional, passível de reutilização, auditoria e evolução.

Cada definição diagnóstica possui identidade própria, ciclo de vida e versionamento.

---

# 2. Separação de responsabilidades

Cada componente do Núcleo de Inteligência possui responsabilidade exclusiva.

O Diagnostic Engine interpreta informações, mas não:

* calcula indicadores;
* mantém conhecimento corporativo;
* define recomendações;
* executa ações corretivas;
* substitui decisões humanas.

Essa separação reduz acoplamento e favorece a evolução independente dos componentes.

---

# 3. Diagnósticos explicáveis

Toda conclusão produzida pelo Diagnostic Engine deve poder ser explicada.

Um diagnóstico nunca deve ser apresentado como uma decisão opaca ("caixa-preta").

A plataforma deve ser capaz de informar:

* quais evidências foram utilizadas;
* quais regras foram avaliadas;
* quais condições foram satisfeitas;
* quais condições não foram satisfeitas;
* quais conhecimentos fundamentaram a interpretação;
* como a conclusão foi obtida.

A explicabilidade é requisito obrigatório da arquitetura.

---

# 4. Evidências rastreáveis

Nenhum diagnóstico deve existir sem evidências identificáveis.

Cada evidência deve possuir origem conhecida e manter vínculo com:

* indicadores;
* dados utilizados;
* contexto avaliado;
* período de referência;
* fontes de informação;
* versão dos ativos utilizados.

A rastreabilidade deve permitir reconstruir integralmente o processo diagnóstico.

---

# 5. Regras explícitas

As regras diagnósticas devem ser definidas de forma explícita, estruturada e governável.

Regras implícitas ou dependentes exclusivamente de código dificultam auditoria, manutenção e evolução.

Sempre que possível, as regras devem constituir ativos institucionais independentes da implementação técnica.

---

# 6. Independência tecnológica

O Diagnostic Engine não depende de:

* linguagem de programação;
* banco de dados;
* mecanismo de persistência;
* framework;
* interface gráfica;
* provedor de inteligência artificial;
* plataforma de execução.

Sua arquitetura permanece válida independentemente das tecnologias adotadas.

---

# 7. Reutilização

Uma definição diagnóstica deve poder ser reutilizada em diferentes:

* organizações;
* unidades;
* períodos;
* dashboards;
* relatórios;
* produtos;
* módulos da plataforma.

A reutilização reduz duplicidade de lógica e aumenta a consistência das interpretações.

---

# 8. Contextualização

Nenhum diagnóstico deve ser interpretado isoladamente.

Toda avaliação deve considerar seu contexto, incluindo:

* organização;
* unidade organizacional;
* período;
* domínio de negócio;
* indicadores disponíveis;
* perfil operacional;
* demais fatores relevantes.

O mesmo conjunto de evidências pode resultar em diagnósticos distintos quando o contexto for diferente.

---

# 9. Versionamento

As definições diagnósticas evoluem ao longo do tempo.

Cada versão deve preservar:

* identidade;
* histórico;
* compatibilidade;
* documentação;
* período de vigência.

Diagnósticos já emitidos permanecem vinculados à versão vigente no momento de sua geração.

---

# 10. Governança

Toda definição diagnóstica deve possuir:

* responsável institucional;
* responsável técnico;
* estado do ciclo de vida;
* critérios de aprovação;
* histórico de alterações;
* referências documentais.

A governança garante controle sobre a evolução do patrimônio intelectual da plataforma.

---

# 11. Integração padronizada

O Diagnostic Engine integra-se aos demais componentes exclusivamente por contratos institucionais.

As integrações devem preservar baixo acoplamento e permitir evolução independente.

Os principais consumidores e fornecedores são:

* Indicator Catalog;
* Knowledge Base;
* Recommendation Engine;
* AI Assistant.

---

# 12. Inteligência assistida

A inteligência artificial constitui um componente complementar do processo diagnóstico.

Ela pode:

* enriquecer interpretações;
* explicar resultados;
* auxiliar investigações;
* apoiar decisões.

Entretanto, a definição institucional dos diagnósticos permanece sob responsabilidade do Diagnostic Engine.

A arquitetura não depende de modelos generativos para produzir diagnósticos oficiais.

---

# 13. Evolução incremental

O Diagnostic Engine deve evoluir continuamente, preservando:

* compatibilidade;
* rastreabilidade;
* governança;
* reutilização;
* estabilidade dos contratos públicos.

Novas capacidades devem ampliar o motor de diagnóstico sem comprometer definições previamente aprovadas.

---

# Síntese

Os princípios apresentados neste documento estabelecem a base arquitetural permanente do Diagnostic Engine.

Toda decisão de modelagem, implementação ou evolução deverá respeitar estes princípios, garantindo que os diagnósticos produzidos permaneçam consistentes, confiáveis, auditáveis e alinhados à arquitetura institucional da Deja Indicadores.
