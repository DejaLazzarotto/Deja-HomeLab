# 10. Integração com Security

## Objetivo

Esta seção define a integração arquitetural entre o Developer Portal e a capacidade Security da Deja Platform.

O objetivo é estabelecer como identidade, autenticação, autorização e proteção de acesso são aplicadas na experiência de consumidores de APIs.

---

# Papel do Security

O Security permanece como a capacidade institucional responsável pela proteção da plataforma.

Suas responsabilidades incluem:

- identidade;
- autenticação;
- autorização;
- gestão de credenciais;
- políticas de segurança;
- proteção de recursos.

---

# Papel do Developer Portal

O Developer Portal atua como camada de experiência.

Suas responsabilidades incluem:

- apresentação de processos de acesso;
- interação com consumidores;
- coleta de solicitações;
- apresentação de informações autorizadas;
- acompanhamento de status.

O Portal não substitui mecanismos de segurança.

---

# Separação de responsabilidades

Modelo:

```text id="8z2m4q"
Consumidor

    |
    v

Developer Portal

    |
    v

Security

    |
    v

Recursos Protegidos