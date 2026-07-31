# 07. Autenticação e Autorização

## Objetivo

Esta seção descreve o modelo de autenticação e autorização aplicado ao API Gateway da Deja Platform.

O objetivo é definir como identidades são validadas, permissões são verificadas e acessos às APIs são controlados.

---

# Visão geral

A segurança do API Gateway é baseada na integração nativa com a capacidade Security da Deja Platform.

O Gateway não implementa mecanismos próprios de identidade.

Ele utiliza os serviços institucionais de:

- autenticação;
- autorização;
- políticas de acesso;
- gerenciamento de credenciais.

---

# Princípio de segurança

Toda chamada recebida pelo API Gateway deve possuir uma identidade conhecida.

Nenhuma API deve ser acessada sem:

- identificação do consumidor;
- validação de credenciais;
- autorização correspondente.

---

# Fluxo de autenticação

O fluxo conceitual é:
