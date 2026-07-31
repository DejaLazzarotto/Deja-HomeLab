# 09. Integração com API Management

## Objetivo

Esta seção define a integração arquitetural entre o Developer Portal e o API Management da Deja Platform.

O objetivo é estabelecer claramente as responsabilidades compartilhadas e separadas entre as duas capacidades, garantindo governança, consistência e evolução controlada do ecossistema de APIs.

---

# Papel do API Management

O API Management permanece como a capacidade institucional responsável pelo gerenciamento do ciclo de vida das APIs.

Suas responsabilidades incluem:

- criação;
- registro;
- validação;
- publicação;
- evolução;
- descontinuação;
- políticas;
- governança.

---

# Papel do Developer Portal

O Developer Portal representa a camada de experiência dos consumidores.

Suas responsabilidades incluem:

- descoberta de APIs;
- apresentação de informações;
- documentação;
- solicitação de acesso;
- acompanhamento de consumo;
- relacionamento com consumidores.

---

# Separação de responsabilidades

Modelo:

```text id="7k3n2v"
                 Consumidor

                     |
                     v

            Developer Portal

                     |
                     v

            API Management

                     |
                     v

             API Gateway

                     |
                     v

                Runtime