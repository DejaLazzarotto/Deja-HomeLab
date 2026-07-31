# 08. Gestão de Consumidores

## Objetivo

Esta seção define o modelo arquitetural de gestão dos consumidores de APIs dentro do Developer Portal da Deja Platform.

O objetivo é estabelecer como consumidores são identificados, registrados, relacionados às APIs e governados durante todo o ciclo de utilização.

---

# Papel institucional

Consumidores representam entidades autorizadas a utilizar recursos disponibilizados pela plataforma.

O Developer Portal fornece a experiência de relacionamento com consumidores, enquanto capacidades institucionais especializadas permanecem responsáveis pelas regras de identidade, segurança e autorização.

---

# Tipos de consumidores

O modelo suporta diferentes categorias:

```text
Consumidores

+----------------------+
| Desenvolvedores      |
+----------------------+
| Aplicações           |
+----------------------+
| Sistemas internos    |
+----------------------+
| Parceiros            |
+----------------------+
| Clientes             |
+----------------------+