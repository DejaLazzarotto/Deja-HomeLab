# 07. Resolução e Precedência

## Objetivo

Esta seção descreve o mecanismo de resolução de configurações e as regras de precedência utilizadas pelo Configuration para determinar o valor final aplicado aos componentes da Deja Platform.

O objetivo é garantir que múltiplas fontes, contextos e versões possam coexistir de forma previsível e controlada.

---

# Conceito de resolução

A resolução de configuração é o processo responsável por transformar diferentes definições configuracionais em uma configuração final efetivamente aplicável.

O Configuration Resolver combina:

- definições base;
- valores específicos;
- contexto operacional;
- ambiente;
- políticas;
- versões ativas.

Resultado:
