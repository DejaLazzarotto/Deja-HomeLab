# 12. Integração com Componentes

## Objetivo

Esta seção descreve como o Security integra-se aos componentes institucionais da Deja Platform.

A integração foi projetada para fornecer capacidades de segurança compartilhadas, mantendo baixo acoplamento e permitindo que cada componente utilize mecanismos padronizados de identidade, autorização, proteção e auditoria.

---

# Princípio de integração

O Security atua como uma camada transversal.

Os componentes da plataforma não implementam mecanismos próprios de segurança quando estes pertencem à responsabilidade institucional do Security.

Em vez disso, utilizam serviços especializados fornecidos pela arquitetura.

---

# Integração com Execution Engine

O Execution Engine utiliza o Security para:

- validar identidade da solicitação;
- verificar permissões de execução;
- controlar acesso a workflows;
- registrar eventos de segurança.

Fluxo:
