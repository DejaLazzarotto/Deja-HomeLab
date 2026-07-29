# 07. Organização da Documentação

## Objetivo

Este documento estabelece o modelo institucional de organização da documentação funcional da Deja Indicadores.

Seu propósito é definir onde cada informação deve ser documentada, evitando duplicidade de conteúdo, preservando a rastreabilidade e facilitando a evolução contínua da documentação.

---

# Princípios

A documentação funcional deve observar os seguintes princípios:

- responsabilidade única para cada documento;
- organização hierárquica;
- rastreabilidade completa;
- reutilização de informações;
- evolução incremental;
- padronização entre produtos da Deja Platform.

Cada documento deve possuir um propósito claramente definido.

---

# Estrutura Geral

A documentação funcional está organizada em duas grandes áreas:

```text
functional-architecture/

functional-specifications/
```

Cada uma possui responsabilidades distintas.

---

# Arquitetura Funcional

A Arquitetura Funcional define o modelo institucional utilizado pelo produto.

Ela contém:

- conceitos;
- organização;
- governança;
- rastreabilidade;
- padrões;
- convenções.

A Arquitetura Funcional é relativamente estável e evolui lentamente ao longo da vida do produto.

---

# Especificações Funcionais

As Especificações Funcionais documentam o comportamento detalhado de cada Feature.

Cada Especificação Funcional representa uma única Feature.

Sua evolução acompanha diretamente a evolução do produto.

---

# Estrutura Recomendada

```text
docs/products/deja-indicadores/

├── functional-architecture/
│   ├── README.md
│   ├── sections/
│   └── ...
│
└── functional-specifications/
    ├── README.md
    │
    ├── FS-001/
    │   ├── README.md
    │   ├── functional-specification.md
    │   └── assets/
    │
    ├── FS-002/
    │   └── ...
    │
    └── ...
```

Cada Feature possui seu próprio diretório, permitindo evolução independente.

---

# Organização por Feature

Cada diretório de Especificação Funcional deverá conter exclusivamente informações referentes à Feature correspondente.

Exemplo:

```text
FS-014/

├── README.md
├── functional-specification.md
├── assets/
└── decisions/
```

Nenhuma Especificação Funcional deverá conter informações pertencentes a outras Features.

---

# Responsabilidade dos Documentos

A separação de responsabilidades segue o modelo abaixo.

| Documento | Responsabilidade |
|-----------|------------------|
| Product Vision | Visão estratégica do produto |
| Product Architecture | Arquitetura conceitual |
| Capability Map | Capacidades do negócio |
| Value Backlog | Planejamento incremental |
| Functional Architecture | Organização funcional |
| Functional Specification | Comportamento detalhado da Feature |
| Arquitetura Técnica | Solução técnica |
| Código | Implementação |
| Testes | Validação |
| Documentação | Material de apoio ao usuário |

Cada informação deve existir em apenas um nível da documentação.

---

# Reutilização

Sempre que uma informação já estiver documentada em outro artefato institucional, ela deverá ser referenciada e não duplicada.

Exemplos:

- uma Capability não deve ser descrita novamente na Feature;
- uma Feature não deve repetir sua Especificação Funcional;
- uma Especificação Funcional não deve repetir a Arquitetura Funcional.

Essa abordagem reduz inconsistências durante a evolução do produto.

---

# Evolução

Novas Features não exigem alterações na Arquitetura Funcional.

Elas apenas acrescentam novas Especificações Funcionais.

Da mesma forma, alterações em uma Feature impactam exclusivamente sua própria documentação, preservando a estabilidade da arquitetura institucional.

---

# Versionamento

Cada documento deve possuir seu próprio histórico de evolução.

A alteração de uma Especificação Funcional não implica alteração da Arquitetura Funcional, salvo quando houver mudança no modelo institucional.

Essa separação permite evolução independente dos diferentes níveis da documentação.

---

# Benefícios

A organização proposta proporciona:

- documentação modular;
- facilidade de navegação;
- menor acoplamento entre documentos;
- evolução incremental;
- rastreabilidade completa;
- redução de redundâncias;
- reutilização institucional.

---

# Considerações Finais

A organização da documentação funcional constitui parte essencial da governança da Deja Platform.

A adoção deste modelo garante consistência entre os diferentes artefatos do produto, facilita sua manutenção e estabelece um padrão reutilizável para futuros produtos desenvolvidos sobre a plataforma.