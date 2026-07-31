# 05. Datasets

## Objetivo

Esta seção define o modelo institucional de persistência dos Datasets dentro do Data Store.

Os Datasets representam o principal ativo de dados da Deja Indicadores e constituem a base para a execução dos indicadores, diagnósticos, recomendações e demais processos do ecossistema de inteligência.

---

# Conceito

Um Dataset representa um conjunto estruturado de dados persistidos pelo Data Store.

Seu conteúdo é produzido pelo Data Pipeline e disponibilizado aos consumidores após cumprir todas as etapas do fluxo institucional.

O Data Store é responsável exclusivamente pela persistência, recuperação, versionamento e governança desses ativos.

---

# Ciclo de Vida

Todo Dataset percorre o seguinte ciclo de vida:

```
Criação
    │
    ▼
Persistência
    │
    ▼
Versionamento
    │
    ▼
Publicação
    │
    ▼
Consumo
    │
    ▼
Arquivamento
```

Cada etapa produz registros próprios de rastreabilidade e auditoria.

---

# Estados Oficiais

Os estados funcionais do Dataset permanecem definidos pelo Data Pipeline:

- Raw;
- Validated;
- Transformed;
- Normalized;
- Enriched;
- Versioned;
- Published.

O Data Store preserva esses estados, mantendo o histórico completo das versões persistidas.

---

# Identificação

Todo Dataset deve possuir um identificador institucional único.

Esse identificador deve ser:

- permanente;
- imutável;
- independente da tecnologia;
- reutilizável em toda a plataforma.

Mudanças no conteúdo do Dataset nunca alteram sua identidade.

---

# Estrutura Lógica

Cada Dataset é composto por:

- Identificador;
- Nome;
- Descrição;
- Esquema;
- Conteúdo;
- Metadados;
- Versão;
- Estado;
- Lineage;
- Informações de Auditoria.

Essa estrutura representa o modelo lógico institucional e não a implementação física.

---

# Versionamento

Todo Dataset é obrigatoriamente versionado.

Cada versão representa um snapshot imutável do conteúdo persistido.

Uma nova publicação gera sempre uma nova versão, preservando integralmente as anteriores.

Esse princípio garante reprodutibilidade e auditoria.

---

# Imutabilidade

Após a publicação, um Dataset torna-se imutável.

Qualquer alteração em seu conteúdo exige a criação de uma nova versão.

Nenhuma versão publicada pode ser modificada diretamente.

---

# Metadados Associados

Cada Dataset possui metadados próprios, incluindo informações como:

- origem;
- domínio;
- classificação;
- responsável;
- data de criação;
- data de publicação;
- políticas de retenção;
- qualidade;
- informações técnicas.

Os metadados são armazenados separadamente do conteúdo.

---

# Relação com o Lineage

Todo Dataset deve possuir registros completos de lineage.

Esses registros permitem identificar:

- origem dos dados;
- fontes utilizadas;
- transformações realizadas;
- versões anteriores;
- ativos derivados;
- consumidores do Dataset.

Essa capacidade é essencial para auditoria e rastreabilidade.

---

# Consulta e Recuperação

Os consumidores podem recuperar Datasets utilizando diferentes critérios, tais como:

- identificador;
- nome;
- versão;
- domínio;
- categoria;
- período;
- estado;
- etiquetas institucionais.

Os mecanismos de consulta são definidos pelos contratos públicos do Data Store.

---

# Governança

A persistência de Datasets deve respeitar as políticas institucionais de:

- retenção;
- classificação;
- controle de acesso;
- auditoria;
- conformidade;
- versionamento.

Nenhum Dataset pode ser disponibilizado fora dessas políticas.

---

# Benefícios

O modelo institucional de Datasets proporciona:

- persistência padronizada;
- versionamento completo;
- recuperação histórica;
- reprodutibilidade;
- rastreabilidade;
- integração transparente com o Data Pipeline;
- independência tecnológica;
- governança consistente.

---

# Próxima Seção

A próxima seção apresenta a arquitetura de persistência dos Metadados, responsáveis por descrever e governar todos os ativos armazenados pelo Data Store.