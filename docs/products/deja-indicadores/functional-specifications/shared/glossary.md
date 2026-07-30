# Glossário Institucional

## Objetivo

Este documento reúne os principais termos utilizados nas Functional Specifications da Deja Indicadores.

Seu objetivo é garantir linguagem uniforme, reduzir ambiguidades e estabelecer um vocabulário comum para todas as Features do produto.

Todos os documentos funcionais deverão utilizar, preferencialmente, as definições aqui estabelecidas.

---

# Termos Institucionais

## Capability (CAP)

Maior unidade de capacidade do produto.

Representa uma competência permanente oferecida pela plataforma ao mercado.

---

## Epic (EP)

Grande iniciativa funcional pertencente a uma Capability.

Agrupa múltiplos módulos funcionais relacionados.

---

## Functional Module (FM)

Conjunto coerente de funcionalidades que atendem a um objetivo específico dentro de uma Epic.

Cada Functional Module organiza uma ou mais Features.

---

## Feature (FE)

Unidade oficial de organização funcional da Deja Indicadores.

Cada Feature possui documentação própria e agrupa todas as suas Functional Specifications.

---

## Functional Function (FF)

Função funcional pertencente a uma Feature.

Representa um comportamento observável pelo usuário ou pelo sistema.

Uma Feature pode conter diversas Functional Functions.

---

## Functional Specification (FS)

Documento que descreve detalhadamente uma Functional Function.

Define comportamento esperado, regras de negócio, fluxos, validações, restrições e critérios de aceitação, permanecendo independente da implementação técnica.

---

## Shared Component

Elemento documental reutilizável por múltiplas Features, como templates, glossário ou componentes comuns.

---

## Template

Modelo institucional utilizado para padronizar a criação de documentos.

Toda nova documentação funcional deverá utilizar os templates oficiais disponibilizados no diretório `shared/templates`.

---

## Critério de Aceitação

Conjunto de condições objetivas que definem quando uma Functional Specification pode ser considerada implementada corretamente.

---

## Regra de Negócio

Restrição ou comportamento funcional que deve ser obrigatoriamente respeitado pela solução.

As regras de negócio são independentes da tecnologia utilizada na implementação.

---

## Fluxo Funcional

Sequência de interações entre usuário e sistema para execução de uma determinada Functional Function.

Pode representar cenários principais, alternativos ou exceções.

---

## Rastreabilidade

Capacidade de relacionar cada elemento funcional às demais camadas da documentação institucional.

A cadeia oficial é:

```
CAP
→ EP
→ FM
→ FE
→ FF
→ FS
→ Arquitetura Técnica
→ Código
→ Testes
→ Documentação
```

---

## Governança

Conjunto de diretrizes responsáveis por garantir a evolução organizada, consistente e auditável da documentação funcional.

---

## Evolução Incremental

Princípio segundo o qual novas funcionalidades são adicionadas por meio de novas Features e Functional Specifications, preservando a estabilidade e a rastreabilidade da documentação existente.