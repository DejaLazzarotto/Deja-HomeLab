# 01. Visão Geral

O Intelligence Core representa o núcleo arquitetural da Deja Indicadores.

Sua responsabilidade é disponibilizar toda a infraestrutura comum utilizada pelos Engines especializados, permitindo que cada componente execute suas responsabilidades de forma independente, coordenada e desacoplada.

O Core não possui conhecimento das regras de negócio implementadas pelos Engines. Sua atuação limita-se à orquestração da infraestrutura necessária para execução do ecossistema de inteligência.

Os principais objetivos do Intelligence Core são:

- fornecer um Runtime institucional único;
- estabelecer um Context compartilhado entre os componentes;
- coordenar Pipelines de execução;
- disponibilizar um Event Bus institucional;
- centralizar Services reutilizáveis;
- manter Registries institucionais;
- controlar o Lifecycle dos componentes;
- oferecer Extension Points para evolução arquitetural;
- prover mecanismos de Observability;
- garantir Traceability ponta a ponta;
- centralizar Configuration institucional;
- disponibilizar APIs públicas para integração.

Essa organização estabelece uma separação clara entre infraestrutura e lógica de negócio.

Como consequência, novos Engines podem ser incorporados ao ecossistema sem alterações estruturais no núcleo, desde que implementem os contratos institucionais definidos pelo Intelligence Core.

O Intelligence Core torna-se, assim, a fundação arquitetural sobre a qual toda a inteligência da Deja Indicadores é construída.