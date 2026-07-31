# 06. Routing e Dispatching

## Objetivo

Esta seção descreve o modelo de roteamento e despacho utilizado pelo API Gateway da Deja Platform.

O objetivo é definir como uma requisição recebida é analisada, resolvida e encaminhada para a capacidade responsável pela execução.

---

# Visão geral

O Routing e Dispatching representam a etapa responsável pela transformação de uma requisição externa em uma chamada interna controlada.

O processo deve garantir:

- resolução correta do destino;
- aplicação das políticas;
- preservação do contexto;
- rastreabilidade;
- baixo acoplamento.

---

# Fluxo de roteamento

O fluxo conceitual é:
