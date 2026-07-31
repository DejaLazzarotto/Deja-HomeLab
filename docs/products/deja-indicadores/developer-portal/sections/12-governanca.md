# 12. Governança

## Objetivo

Esta seção define os princípios e mecanismos de governança aplicados ao Developer Portal da Deja Platform.

O objetivo é garantir que a disponibilização de APIs, consumidores, documentação e experiências de integração siga padrões institucionais controlados.

---

# Papel da governança

A governança do Developer Portal garante que o ecossistema de APIs permaneça:

- organizado;
- seguro;
- rastreável;
- sustentável;
- alinhado à arquitetura da plataforma.

---

# Princípios de governança

## Controle institucional

O Developer Portal opera dentro das regras definidas pela Deja Platform.

Nenhuma capacidade deve funcionar fora dos mecanismos oficiais de:

- registro;
- publicação;
- segurança;
- auditoria.

---

## Fonte oficial de informação

O Portal deve consumir informações provenientes das capacidades responsáveis.

Fontes:

- API Registry;
- API Management;
- Security;
- Configuration.

O Portal não deve criar registros independentes de APIs.

---

## Publicação controlada

Somente APIs aprovadas podem ser disponibilizadas aos consumidores.

Fluxo:

```text id="g5w2vk"
API criada

    |
    v

Registro

    |
    v

Validação

    |
    v

Governança

    |
    v

Publicação

    |
    v

Developer Portal