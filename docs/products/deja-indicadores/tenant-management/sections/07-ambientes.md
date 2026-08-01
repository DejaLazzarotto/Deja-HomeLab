# 7. Ambientes

## Objetivo

Esta seção define o modelo institucional de Ambientes da Deja Platform, estabelecendo como os diferentes contextos operacionais de um Tenant são organizados, administrados e isolados.

Os Ambientes permitem que um mesmo Tenant mantenha múltiplas instâncias operacionais independentes, suportando diferentes fases do ciclo de vida das aplicações e operações.

---

# Conceito

Um Ambiente representa uma instância operacional pertencente exclusivamente a um Tenant.

Cada Ambiente possui identidade própria, configurações independentes e recursos isolados.

O Ambiente não substitui o Tenant; ele representa um subconjunto operacional dentro do domínio daquele Tenant.

---

# Hierarquia

A relação institucional é definida da seguinte forma:

```text
Organização
    │
    └── Tenant
            │
            ├── Ambiente
            ├── Ambiente
            ├── Ambiente
            └── Ambiente
```

Um Tenant pode possuir um ou vários Ambientes.

Cada Ambiente pertence exclusivamente a um único Tenant.

---

# Ambientes Padrão

A arquitetura prevê, como referência, os seguintes Ambientes:

- Development
- Homologation
- Production
- Sandbox

Outros Ambientes poderão ser definidos conforme necessidades específicas de cada Organização, respeitando as políticas institucionais.

---

# Responsabilidades

Compete ao Ambiente:

- manter configurações específicas;
- isolar recursos operacionais;
- identificar execuções;
- separar dados operacionais;
- definir políticas locais;
- suportar diferentes estágios de implantação.

Toda execução institucional ocorre associada a um Ambiente válido.

---

# Isolamento

Os Ambientes são logicamente independentes entre si.

Essa independência abrange:

- configurações;
- execuções;
- históricos;
- eventos;
- métricas;
- logs;
- integrações;
- artefatos temporários.

Não existe compartilhamento implícito entre Ambientes.

Qualquer sincronização deverá ocorrer por mecanismos institucionais específicos e auditáveis.

---

# Identidade

Cada Ambiente possui um identificador institucional único dentro do Tenant ao qual pertence.

Os identificadores permanecem imutáveis durante todo o ciclo de vida do Ambiente.

Alterações em nome, descrição ou metadados não modificam sua identidade.

---

# Ciclo de Vida

Os Ambientes seguem um ciclo de vida independente:

```text
Provisioning

↓

Active

↓

Maintenance

↓

Suspended

↓

Archived

↓

Removed
```

As transições de estado são controladas pelo Tenant Lifecycle Manager e registradas pelos mecanismos institucionais de rastreabilidade.

---

# Provisionamento

O provisionamento de um Ambiente envolve:

- criação estrutural;
- associação ao Tenant;
- inicialização das configurações;
- integração com Security;
- integração com Configuration;
- integração com Observability;
- registro institucional.

Após o provisionamento, o Ambiente torna-se apto a receber aplicações e operações.

---

# Integrações

Os Ambientes são utilizados por diversos componentes da plataforma, incluindo:

- API Gateway;
- API Management;
- Security;
- Configuration;
- Observability;
- Execution Engine;
- Marketplace;
- Developer Portal;
- Module Platform.

Todos os componentes utilizam o Ambiente como parte do contexto operacional.

---

# Governança

A criação, alteração e remoção de Ambientes deve ocorrer exclusivamente pelos serviços oficiais do Tenant Management.

Toda operação deve produzir:

- auditoria;
- histórico permanente;
- rastreabilidade;
- eventos institucionais.

Operações diretas sobre estruturas internas dos Ambientes não são permitidas.

---

# Benefícios

O modelo institucional de Ambientes proporciona:

- segregação operacional;
- segurança;
- previsibilidade;
- facilidade de implantação;
- suporte a pipelines de entrega;
- administração simplificada;
- reutilização da infraestrutura.

---

# Resultado Esperado

Ao final desta definição, a Deja Platform estabelece um modelo institucional de Ambientes consistente e reutilizável, permitindo que cada Tenant mantenha múltiplos contextos operacionais independentes, preservando isolamento, governança e rastreabilidade em toda a plataforma.