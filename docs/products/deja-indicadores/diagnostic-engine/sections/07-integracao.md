# 07. Integração

## Objetivo

Este documento define como o Diagnostic Engine integra-se aos demais componentes da Deja Indicadores, estabelecendo os contratos institucionais de entrada e saída necessários para a geração de diagnósticos gerenciais.

As integrações descritas neste documento seguem os princípios de baixo acoplamento, alta coesão, reutilização e rastreabilidade adotados pela plataforma.

---

# 1. Visão Geral

O Diagnostic Engine ocupa a camada de interpretação do Núcleo de Inteligência.

Seu papel é consumir indicadores, evidências e conhecimento institucional, produzindo diagnósticos estruturados que poderão ser utilizados por outros componentes da plataforma.

O fluxo institucional é representado por:

```text
Fontes de Dados
        │
        ▼
Indicator Catalog
        │
        ▼
Knowledge Base
        │
        ▼
Diagnostic Engine
        │
        ▼
Recommendation Engine
        │
        ▼
AI Assistant
```

Cada componente possui responsabilidades exclusivas e comunica-se por contratos institucionais bem definidos.

---

# 2. Integração com o Indicator Catalog

O Indicator Catalog é o fornecedor oficial das informações quantitativas utilizadas pelo Diagnostic Engine.

Entre os ativos consumidos destacam-se:

* definições de indicadores;
* valores calculados;
* períodos de referência;
* unidades de medida;
* classificações;
* metadados;
* qualidade dos dados;
* histórico de indicadores.

O Diagnostic Engine nunca recalcula indicadores.

Sua responsabilidade limita-se à interpretação dos resultados produzidos pelo Indicator Catalog.

---

# 3. Integração com a Knowledge Base

A Knowledge Base fornece o conhecimento institucional necessário para contextualizar as avaliações.

O Diagnostic Engine pode utilizar:

* conceitos;
* definições;
* metodologias;
* interpretações;
* critérios;
* políticas corporativas;
* referências normativas;
* demais itens de conhecimento.

Essa integração permite que o diagnóstico utilize conhecimento corporativo reutilizável sem incorporá-lo diretamente às regras diagnósticas.

---

# 4. Integração com o Recommendation Engine

Após a conclusão da avaliação, o Diagnostic Engine disponibiliza seus resultados ao Recommendation Engine.

Entre as informações compartilhadas estão:

* diagnóstico produzido;
* classificação;
* severidade;
* impacto;
* prioridade;
* nível de confiança;
* contexto;
* explicação;
* evidências utilizadas.

O Recommendation Engine permanece responsável pela seleção e geração das ações recomendadas.

Essa separação preserva a independência entre interpretação e prescrição.

---

# 5. Integração com o AI Assistant

O AI Assistant utiliza os diagnósticos produzidos para apoiar a interação com os usuários.

Pode utilizar:

* explicações;
* classificações;
* evidências;
* contexto;
* histórico;
* nível de confiança;
* rastreabilidade.

O AI Assistant não substitui o processo institucional de avaliação nem altera os diagnósticos produzidos.

Sua função é facilitar compreensão, exploração e comunicação das informações.

---

# 6. Integração com Fontes de Dados

O Diagnostic Engine não acessa diretamente bancos de dados, planilhas ou sistemas externos.

Todo acesso aos dados ocorre por meio dos componentes responsáveis pelo fornecimento das evidências necessárias à avaliação.

Essa abordagem reduz acoplamento e preserva independência tecnológica.

---

# 7. Contratos Institucionais

Todas as integrações devem ocorrer por contratos explícitos.

Os contratos devem definir:

* estrutura das entradas;
* estrutura das saídas;
* identificadores institucionais;
* versionamento;
* políticas de compatibilidade;
* tratamento de erros;
* requisitos mínimos de rastreabilidade.

Os contratos não devem depender de tecnologias específicas de transporte ou persistência.

---

# 8. Fluxo de Integração

O processo completo pode ser representado pelo seguinte fluxo:

```text
Indicator Catalog
        │
        ▼
Knowledge Base
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
Diagnostic Instance
        │
        ├──────────────► Recommendation Engine
        │
        └──────────────► AI Assistant
```

Cada componente executa apenas sua responsabilidade específica.

---

# 9. Independência Arquitetural

As integrações devem preservar independência em relação a:

* banco de dados;
* linguagem de programação;
* framework;
* API específica;
* mensageria;
* inteligência artificial;
* tecnologia de persistência.

Essa independência garante que os contratos institucionais permaneçam estáveis mesmo diante da evolução tecnológica da plataforma.

---

# 10. Evolução das Integrações

Novas integrações poderão ser adicionadas futuramente, desde que:

* utilizem contratos institucionais;
* preservem rastreabilidade;
* mantenham compatibilidade;
* não comprometam o baixo acoplamento;
* respeitem a arquitetura do Núcleo de Inteligência.

A expansão das integrações deverá fortalecer a reutilização dos diagnósticos produzidos pelo Diagnostic Engine sem alterar suas responsabilidades fundamentais.

---

# Síntese

O Diagnostic Engine atua como o componente responsável por interpretar indicadores e conhecimento institucional, transformando-os em diagnósticos reutilizáveis.

Sua integração com o Indicator Catalog, a Knowledge Base, o Recommendation Engine e o AI Assistant estabelece um fluxo arquitetural coeso, modular e governado, permitindo que os diagnósticos se tornem ativos compartilhados por toda a Deja Indicadores.
