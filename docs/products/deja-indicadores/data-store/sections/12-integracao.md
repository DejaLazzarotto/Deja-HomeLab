# 12. Integração

## Objetivo

Esta seção define a arquitetura institucional de integração do Data Store com os demais componentes da Deja Indicadores.

O objetivo é garantir que toda comunicação com a camada de persistência ocorra de forma padronizada, desacoplada e independente das tecnologias de armazenamento adotadas pela implementação.

---

# Princípios

A integração do Data Store baseia-se nos seguintes princípios:

- contratos públicos estáveis;
- independência tecnológica;
- baixo acoplamento;
- alta coesão;
- interoperabilidade;
- rastreabilidade completa;
- observabilidade integrada;
- evolução incremental.

Nenhum componente da plataforma possui acesso direto à infraestrutura física de persistência.

---

# Modelo de Integração

Toda interação com o Data Store ocorre por meio da Data Store Public API.

O fluxo arquitetural é representado da seguinte forma:

```
Componente Consumidor
          │
          ▼
   Data Store Public API
          │
          ▼
   Serviços Institucionais
          │
          ▼
  Camada de Persistência
          │
          ▼
Infraestrutura de Armazenamento
```

Essa organização preserva a independência entre consumidores e mecanismos de armazenamento.

---

# Componentes Integrados

O Data Store integra-se diretamente com:

- Data Pipeline;
- Intelligence Core;
- Indicator Catalog;
- Knowledge Base;
- Diagnostic Engine;
- Decision Engine;
- Recommendation Engine;
- Runtime Institucional;
- Serviços de Observabilidade;
- Serviços de Governança.

Todos os componentes utilizam os mesmos contratos públicos.

---

# Integração com o Data Pipeline

O Data Pipeline é o principal produtor de ativos persistidos.

Entre as operações realizadas estão:

- persistência de Datasets;
- publicação de versões;
- registro de metadados;
- atualização do Lineage;
- armazenamento de artefatos.

O Data Pipeline não acessa diretamente mecanismos físicos de armazenamento.

---

# Integração com o Intelligence Core

O Intelligence Core consome os ativos persistidos e também produz novos ativos derivados.

Entre eles:

- diagnósticos;
- recomendações;
- resultados analíticos;
- artefatos especializados.

Toda persistência ocorre através do Data Store.

---

# Integração com o Indicator Catalog

O Indicator Catalog utiliza o Data Store para:

- persistência de definições;
- armazenamento de metadados;
- versionamento de indicadores;
- recuperação de versões históricas.

Essa integração preserva a rastreabilidade das definições institucionais.

---

# Integração com a Knowledge Base

A Knowledge Base utiliza o Data Store para armazenar:

- itens de conhecimento;
- metadados;
- versões;
- relacionamentos;
- artefatos associados.

Os mecanismos de persistência permanecem transparentes para a Knowledge Base.

---

# Integração com os Engines

Diagnostic Engine, Decision Engine e Recommendation Engine utilizam o Data Store para:

- recuperar Datasets;
- consultar metadados;
- persistir resultados;
- registrar artefatos;
- atualizar Lineage;
- manter auditoria.

Os Engines permanecem desacoplados da infraestrutura de armazenamento.

---

# Contratos Públicos

Os contratos públicos representam a única forma suportada de interação com o Data Store.

Esses contratos definem operações como:

- persistir;
- recuperar;
- consultar;
- versionar;
- publicar;
- arquivar;
- registrar Lineage;
- registrar Auditoria.

Alterações internas de implementação não devem modificar esses contratos.

---

# Evolução da Integração

Novos componentes poderão integrar-se ao Data Store utilizando os mesmos contratos públicos.

Essa abordagem permite expansão do ecossistema sem impacto sobre os consumidores existentes.

---

# Benefícios

O modelo institucional de integração proporciona:

- desacoplamento arquitetural;
- interoperabilidade;
- independência tecnológica;
- reutilização dos serviços de persistência;
- estabilidade dos contratos;
- facilidade de evolução;
- integração consistente entre todos os componentes;
- redução da complexidade operacional.

---

# Próxima Seção

A próxima seção apresenta a arquitetura de Rastreabilidade, responsável por registrar e acompanhar todas as operações relevantes executadas pelo Data Store ao longo do ciclo de vida dos ativos persistidos.