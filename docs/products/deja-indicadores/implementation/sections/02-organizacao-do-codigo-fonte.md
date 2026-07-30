# 02. Organização do Código-Fonte

## Objetivo

Este documento estabelece a organização oficial do código-fonte da Deja Indicadores.

A estrutura do projeto deve favorecer legibilidade, modularidade, reutilização, facilidade de manutenção e evolução incremental, mantendo alinhamento com a Arquitetura Técnica e com os padrões institucionais da Deja Platform.

---

## Princípios

A organização do código deve observar os seguintes princípios:

- separação clara de responsabilidades;
- organização por domínio funcional;
- baixo acoplamento entre módulos;
- alta coesão interna;
- reutilização de componentes compartilhados;
- independência entre camadas;
- facilidade para testes automatizados;
- evolução incremental da base de código.

---

## Organização Geral

O código-fonte deverá ser estruturado em módulos claramente definidos, refletindo as responsabilidades identificadas na Arquitetura Técnica.

A estrutura física do projeto deve facilitar a localização dos componentes e reduzir dependências desnecessárias entre áreas distintas da aplicação.

Sempre que possível, os módulos devem representar capacidades do produto, evitando organizações baseadas exclusivamente em tecnologias ou frameworks.

---

## Componentes Compartilhados

Funcionalidades reutilizáveis devem ser concentradas em módulos compartilhados, permitindo seu uso por diferentes partes da aplicação.

Exemplos incluem:

- utilitários;
- componentes comuns;
- contratos;
- modelos compartilhados;
- serviços reutilizáveis;
- infraestrutura técnica.

Componentes específicos do domínio da Deja Indicadores não devem ser promovidos para módulos compartilhados sem análise arquitetural.

---

## Dependências

As dependências entre módulos devem seguir fluxo unidirecional.

Cada módulo deve conhecer apenas os contratos públicos necessários para sua operação, evitando acesso direto às implementações internas de outros módulos.

Dependências circulares são consideradas violações arquiteturais e devem ser eliminadas.

---

## Evolução

A organização do código-fonte poderá evoluir conforme novas capacidades forem incorporadas ao produto.

Entretanto, alterações estruturais deverão preservar:

- compatibilidade arquitetural;
- padronização institucional;
- rastreabilidade;
- facilidade de manutenção;
- documentação atualizada.

---

## Governança

Toda reorganização significativa da estrutura do código deverá ser previamente documentada na Arquitetura de Implementação e aprovada conforme o processo institucional de governança arquitetural.