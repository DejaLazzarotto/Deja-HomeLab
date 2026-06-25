# ADR-003 — Padrão de Publicação de Aplicações

## Status

Accepted

## Data

2026-06-25

---

# Contexto

A Deja Platform hospeda múltiplas aplicações desenvolvidas de forma independente.

À medida que novos projetos forem incorporados, torna-se necessário estabelecer um padrão para organização, publicação e documentação das aplicações.

Sem uma convenção definida, a plataforma tende a crescer de forma inconsistente, dificultando manutenção, operação e evolução.

---

# Decisão

Toda aplicação incorporada à Deja Platform deverá seguir um conjunto mínimo de requisitos arquiteturais antes de ser considerada apta para produção.

---

# Estrutura de Diretórios

Aplicações web deverão ser armazenadas em:

```text
/var/www/deja/apps
```

Dados persistentes deverão utilizar:

```text
/var/www/deja/storage
```

Arquivos públicos compartilhados deverão utilizar:

```text
/var/www/deja/public
```

---

# Publicação

Toda aplicação deverá ser publicada através do NGINX.

O acesso direto a portas internas não deverá ser utilizado como forma oficial de publicação, salvo quando existir justificativa documentada em uma ADR.

---

# Documentação Obrigatória

Cada aplicação deverá possuir, no mínimo:

* descrição funcional;
* estratégia de deploy;
* dependências;
* localização na plataforma;
* responsável técnico;
* repositório Git.

---

# Versionamento

Toda publicação deverá estar associada a um commit Git.

Entregas relevantes deverão utilizar tags de versão.

---

# Segurança

Aplicações publicadas deverão:

* utilizar HTTPS;
* permanecer isoladas das demais aplicações;
* expor apenas os serviços necessários;
* utilizar autenticação quando aplicável.

---

# Operação

Toda aplicação deverá possuir:

* procedimento de atualização;
* procedimento de rollback;
* estratégia de backup, quando necessária;
* documentação operacional.

---

# Consequências

## Benefícios

* Padronização da plataforma.
* Facilidade para manutenção.
* Facilidade para incorporar novos projetos.
* Melhor documentação.
* Redução do risco operacional.

## Desvantagens

* Maior disciplina durante o desenvolvimento.
* Necessidade de manter documentação atualizada.

---

# Relação com outras ADRs

* ADR-001 — Platform Architecture
* ADR-002 — NGINX como Edge Layer
