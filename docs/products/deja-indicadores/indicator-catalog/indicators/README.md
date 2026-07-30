# Indicadores

## Visão Geral

O diretório **indicators/** concentra a documentação individual de todos os indicadores suportados pela Deja Indicadores.

Cada indicador representa uma unidade documental independente, contendo todas as informações necessárias para sua especificação funcional, implementação, validação e evolução.

Essa organização facilita a manutenção do catálogo, preserva a rastreabilidade institucional e permite que novos indicadores sejam incorporados ao produto de forma incremental.

---

# Organização

Cada indicador deverá possuir um diretório próprio.

Exemplo:

```text
indicators/

├── IND-001-faturamento/
├── IND-002-ticket-medio/
├── IND-003-margem-bruta/
└── ...
```

O identificador institucional (**IND-XXX**) permanece imutável durante todo o ciclo de vida do indicador, enquanto o nome descritivo facilita a navegação pela documentação.

---

# Estrutura de um Indicador

Cada diretório de indicador deverá seguir a estrutura oficial definida pelo catálogo.

Exemplo:

```text
IND-001-faturamento/

├── README.md
├── indicator.md
├── calculation.md
├── implementation.md
├── tests.md
└── changelog.md
```

Cada documento possui uma responsabilidade específica e complementa os demais, formando a documentação completa do indicador.

---

# Padronização

Todos os indicadores deverão utilizar:

- o `indicator-template.md`;
- o `calculation-template.md`;
- o glossário institucional;
- as convenções definidas pelo Catálogo Oficial de Indicadores.

Não serão admitidas estruturas documentais distintas sem aprovação formal da governança do produto.

---

# Rastreabilidade

Cada indicador deverá manter vínculo explícito com:

- Capability (CAP);
- Epic (EP);
- Functional Module (FM);
- Feature (FE);
- Functional Flow (FF);
- Functional Specification (FS);
- Arquitetura Técnica;
- Arquitetura de Implementação;
- código-fonte;
- testes automatizados.

Essa rastreabilidade garante total transparência sobre a origem e a evolução de cada indicador.

---

# Evolução

Novos indicadores poderão ser adicionados ao diretório **indicators/** sem necessidade de reorganizar a estrutura existente.

A padronização definida neste documento assegura escalabilidade, governança e consistência para todo o Catálogo Oficial de Indicadores.