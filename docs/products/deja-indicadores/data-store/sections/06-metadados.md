# 06. Metadados

## Objetivo

Esta seção define o modelo institucional de persistência dos Metadados no Data Store.

Os metadados representam a descrição formal dos ativos armazenados pela plataforma, permitindo sua identificação, classificação, governança, descoberta e utilização pelos componentes do ecossistema.

---

# Conceito

Metadados são informações que descrevem um ativo persistido.

Eles não representam o conteúdo do ativo, mas sim seus atributos, contexto e características operacionais.

Todo ativo armazenado no Data Store deve possuir metadados associados.

---

# Finalidades

Os metadados possuem diversas finalidades dentro da plataforma, entre elas:

- identificação;
- classificação;
- documentação;
- descoberta;
- rastreabilidade;
- governança;
- auditoria;
- integração;
- observabilidade.

Sua existência é obrigatória para todos os ativos institucionais.

---

# Estrutura Lógica

Os metadados podem conter informações como:

- identificador;
- nome;
- descrição;
- domínio funcional;
- categoria;
- proprietário;
- origem;
- data de criação;
- data de atualização;
- versão;
- estado;
- etiquetas;
- políticas aplicáveis.

A estrutura poderá evoluir ao longo do tempo sem comprometer a compatibilidade arquitetural.

---

# Classificação

Os metadados permitem classificar os ativos segundo diferentes perspectivas.

Exemplos:

- domínio de negócio;
- área organizacional;
- tipo de ativo;
- criticidade;
- confidencialidade;
- finalidade;
- ciclo de vida.

Uma mesma classificação pode ser utilizada por diferentes componentes da plataforma.

---

# Independência do Conteúdo

Os metadados são armazenados separadamente do conteúdo do ativo.

Essa separação proporciona:

- consultas mais eficientes;
- indexação otimizada;
- evolução independente;
- menor acoplamento;
- melhor governança.

Alterações nos metadados não implicam, necessariamente, alterações no conteúdo persistido.

---

# Versionamento

Os metadados acompanham o versionamento do ativo ao qual estão associados.

Cada versão publicada preserva seus respectivos metadados, permitindo reconstrução completa do contexto histórico.

---

# Integração com o Lineage

Os metadados complementam as informações de lineage.

Enquanto o Lineage descreve as relações entre ativos, os metadados descrevem as características individuais de cada um.

Essas duas capacidades são complementares e inseparáveis na arquitetura.

---

# Descoberta de Ativos

Os metadados possibilitam mecanismos de descoberta e navegação.

Os consumidores poderão localizar ativos utilizando critérios como:

- nome;
- domínio;
- categoria;
- etiquetas;
- proprietário;
- estado;
- período;
- versão.

Os mecanismos específicos de busca pertencem aos contratos públicos da plataforma.

---

# Governança

Os metadados são fundamentais para a aplicação das políticas institucionais de governança.

Entre elas:

- retenção;
- classificação;
- controle de acesso;
- auditoria;
- conformidade;
- qualidade dos dados.

A ausência de metadados inviabiliza a governança adequada dos ativos.

---

# Benefícios

O modelo institucional de metadados proporciona:

- identificação padronizada dos ativos;
- descoberta simplificada;
- melhor organização dos dados;
- rastreabilidade ampliada;
- suporte à auditoria;
- governança consistente;
- integração entre componentes;
- evolução independente do conteúdo.

---

# Próxima Seção

A próxima seção apresenta o modelo institucional de Versionamento, responsável por garantir a preservação histórica e a reprodutibilidade dos ativos persistidos pelo Data Store.