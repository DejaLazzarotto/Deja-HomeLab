# 04. Modelo do Portal

## Objetivo

Esta seção define o modelo arquitetural do Developer Portal da Deja Platform.

O modelo estabelece os principais elementos que compõem a capacidade, suas responsabilidades e os fluxos institucionais envolvidos na experiência dos consumidores de APIs.

---

# Visão conceitual

O Developer Portal é uma camada de experiência construída sobre as capacidades de governança e execução da plataforma.

Ele não possui responsabilidade sobre processamento de APIs, mas organiza e apresenta os recursos disponíveis para consumidores autorizados.

Modelo:

```text
+------------------------------------------------+
|                 Consumidores                   |
+------------------------------------------------+
                       |
                       v
+------------------------------------------------+
|              Developer Portal                  |
|                                                |
|  +---------------+  +----------------------+   |
|  | API Catalog   |  | Documentation        |   |
|  +---------------+  +----------------------+   |
|                                                |
|  +---------------+  +----------------------+   |
|  | Consumer     |  | Access Experience    |   |
|  | Management   |  |                      |   |
|  +---------------+  +----------------------+   |
+------------------------------------------------+
                       |
                       v
+------------------------------------------------+
|            Platform Governance Layer            |
|                                                |
| API Management | API Registry | Security       |
+------------------------------------------------+
                       |
                       v
+------------------------------------------------+
|              Runtime Execution Layer            |
|                                                |
| API Gateway | Services | Runtime               |
+------------------------------------------------+