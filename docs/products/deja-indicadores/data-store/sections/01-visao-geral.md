# 01. Visão Geral

## Objetivo

O Data Store estabelece a arquitetura institucional responsável pela persistência dos ativos da Deja Indicadores.

Sua finalidade é oferecer uma camada única de armazenamento capaz de preservar dados, metadados e artefatos produzidos pelo ecossistema da plataforma, mantendo independência das tecnologias de persistência utilizadas.

O Data Store representa a única infraestrutura oficial de armazenamento permanente da plataforma.

---

# Papel na Arquitetura

Dentro da arquitetura da Deja Indicadores, o Data Store ocupa a camada de persistência institucional.

Sua responsabilidade é receber ativos produzidos pelos componentes da plataforma, armazená-los de forma consistente, disponibilizá-los para consulta e preservar seu histórico completo durante todo o ciclo de vida.

O Data Store não executa processamento de negócio.

Sua responsabilidade limita-se ao armazenamento, recuperação e governança dos ativos persistidos.

---

# Ativos Persistidos

O Data Store é responsável pelo armazenamento dos seguintes ativos:

- Datasets;
- Metadados;
- Configurações;
- Artefatos de Execução;
- Informações de Versionamento;
- Dados de Lineage;
- Registros de Auditoria;
- Objetos Operacionais;
- Catálogos Persistidos;
- Dados de Observabilidade.

Cada ativo possui ciclo de vida próprio, identificação única e políticas específicas de retenção e governança.

---

# Independência Tecnológica

Um dos princípios fundamentais do Data Store é a completa independência da tecnologia de armazenamento.

A arquitetura não estabelece dependência de:

- banco de dados relacional;
- banco NoSQL;
- armazenamento orientado a objetos;
- armazenamento em arquivos;
- data lake;
- data warehouse;
- tecnologias em nuvem;
- fornecedores específicos.

Essas decisões pertencem exclusivamente à implementação.

Os consumidores interagem apenas com contratos públicos.

---

# Relação com o Data Pipeline

O Data Pipeline prepara os dados.

O Data Store persiste os dados preparados.

O fluxo arquitetural institucional torna-se:

```
Fontes
   │
   ▼
Data Pipeline
   │
   ▼
Data Store
   │
   ▼
Intelligence Core
   │
   ▼
Engines Especializados
```

Essa separação garante baixo acoplamento entre preparação de dados e persistência.

---

# Papel no Ecossistema

O Data Store fornece serviços de persistência para:

- Data Pipeline;
- Intelligence Core;
- Indicator Catalog;
- Knowledge Base;
- Diagnostic Engine;
- Decision Engine;
- Recommendation Engine;
- Serviços Institucionais.

Nenhum desses componentes conhece detalhes da infraestrutura física de armazenamento.

---

# Benefícios Arquiteturais

A adoção do Data Store proporciona:

- armazenamento centralizado;
- versionamento consistente;
- lineage completo;
- rastreabilidade institucional;
- independência tecnológica;
- reutilização de ativos;
- governança de dados;
- evolução incremental da infraestrutura;
- maior confiabilidade operacional;
- redução do acoplamento arquitetural.

---

# Escopo da Arquitetura

Esta arquitetura define:

- organização da persistência;
- modelos lógicos de armazenamento;
- contratos públicos;
- responsabilidades institucionais;
- integração com o ecossistema;
- governança da persistência;
- observabilidade;
- rastreabilidade;
- evolução da infraestrutura.

Os detalhes específicos de implementação permanecem fora do escopo desta documentação.

---

# Próxima Seção

A próxima seção apresenta os princípios arquiteturais que orientam toda a evolução do Data Store institucional.