# 06. Catálogo de APIs

## Objetivo

Esta seção define o modelo arquitetural do catálogo de APIs do Developer Portal da Deja Platform.

O catálogo representa a visão organizada e consumível das APIs disponibilizadas pela plataforma, permitindo descoberta, consulta e entendimento dos recursos disponíveis pelos consumidores autorizados.

---

# Papel institucional

O Catálogo de APIs estabelece a camada oficial de descoberta das APIs da Deja Platform.

Sua responsabilidade é apresentar informações confiáveis sobre:

- APIs disponíveis;
- capacidades associadas;
- versões;
- documentação;
- estado de publicação;
- regras de consumo.

O catálogo não substitui o API Registry.

O API Registry permanece como fonte institucional dos registros de APIs.

---

# Relação com API Registry

Modelo:

```text
+----------------+
| API Registry   |
| Fonte oficial  |
+----------------+
        |
        v
+----------------+
| API Catalog    |
| Experiência    |
| de descoberta  |
+----------------+
        |
        v
+----------------+
| Consumidores   |
+----------------+