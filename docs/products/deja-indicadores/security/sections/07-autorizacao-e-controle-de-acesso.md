# 07. Autorização e Controle de Acesso

## Objetivo

Esta seção descreve a arquitetura institucional de autorização e controle de acesso do Security da Deja Platform.

A autorização é responsável por determinar quais operações uma identidade autenticada pode executar sobre determinados recursos, considerando políticas, contexto e regras institucionais.

---

# Conceito de autorização

A autorização representa a decisão de permitir ou negar uma operação solicitada.

Enquanto a autenticação responde:

> Quem é a entidade?

A autorização responde:

> O que essa entidade pode fazer?

---

# Modelo de autorização

O modelo considera a relação entre:

- identidade;
- recurso;
- ação;
- contexto;
- política;
- decisão.

Representação conceitual:
