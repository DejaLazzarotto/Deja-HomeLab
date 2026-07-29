# Mapa de Capacidades da Deja Indicadores

**Versão:** 1.0  
**Status:** Aprovado  
**Classificação:** Documento Mestre

---

# 1. Objetivo

Este documento estabelece o modelo institucional utilizado para representar as capacidades da Deja Indicadores.

O Mapa de Capacidades constitui a principal referência para a organização do conhecimento do produto, permitindo sua decomposição de forma hierárquica e rastreável.

Seu propósito é garantir que toda evolução do produto tenha origem em capacidades claramente definidas antes da criação do Backlog de Valor.

---

# 2. Conceito de Capacidade

Uma capacidade representa uma competência permanente do produto para realizar uma determinada atividade de negócio.

Capacidades descrevem **o que o produto é capaz de fazer**, independentemente de tecnologia, interface, arquitetura de software ou implementação.

Capacidades não representam:

- telas;
- funcionalidades isoladas;
- APIs;
- componentes técnicos;
- módulos de software.

---

# 3. Modelo Hierárquico

Toda capacidade poderá ser decomposta segundo a seguinte estrutura institucional.

```text
Produto
    ↓
Capacidade
    ↓
Subcapacidade
    ↓
Serviço de Negócio
```

Essa decomposição representa a estrutura oficial da Deja Indicadores.

---

# 4. Regras de Decomposição

A decomposição deverá obedecer aos seguintes princípios:

- cada capacidade possui um único propósito de negócio;
- uma capacidade pode possuir diversas subcapacidades;
- uma subcapacidade pode disponibilizar diversos serviços de negócio;
- serviços representam as menores unidades utilizadas para construção do Backlog de Valor;
- não é permitido duplicar responsabilidades entre capacidades.

---

# 5. Rastreabilidade

Toda implementação deverá possuir origem em um Serviço de Negócio identificado no Mapa de Capacidades.

A rastreabilidade oficial seguirá o fluxo abaixo.

```text
Capacidade
        ↓
Subcapacidade
        ↓
Serviço de Negócio
        ↓
Backlog de Valor
        ↓
Arquitetura Funcional
        ↓
Especificação Funcional
        ↓
Implementação
        ↓
Testes
        ↓
Documentação
```

Nenhum item do Backlog poderá existir sem vínculo com uma capacidade previamente definida.

---

# 6. Relação com a Arquitetura do Produto

O Mapa de Capacidades complementa a Arquitetura do Produto.

Enquanto a Arquitetura descreve a organização estrutural da Deja Indicadores, o Mapa de Capacidades descreve a organização do conhecimento de negócio.

Os dois documentos são complementares e devem evoluir de forma consistente.

---

# 7. Relação com o Backlog de Valor

O Backlog de Valor será derivado exclusivamente dos Serviços de Negócio identificados no Mapa de Capacidades.

Essa abordagem garante que todas as entregas possuam alinhamento com os objetivos estratégicos do produto.

---

# 8. Evolução do Modelo

Novas capacidades poderão ser adicionadas conforme a evolução da Deja Indicadores.

Entretanto, toda nova capacidade deverá:

- possuir justificativa de negócio;
- respeitar os princípios arquiteturais definidos para o produto;
- manter a rastreabilidade institucional;
- preservar a separação entre Produto e Plataforma.

---

# 9. Próxima Etapa

A próxima etapa consiste na construção do documento **01-modelo-de-capacidades.md**, que apresentará a árvore institucional completa das capacidades da Deja Indicadores.

Essa árvore será utilizada como referência para a elaboração do Backlog de Valor e das futuras Arquiteturas Funcionais.