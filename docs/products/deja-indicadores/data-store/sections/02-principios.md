# 02. Princípios

## Objetivo

Esta seção estabelece os princípios arquiteturais que orientam a evolução do Data Store da Deja Indicadores.

Esses princípios são mandatórios para qualquer implementação da camada de persistência, independentemente das tecnologias utilizadas.

---

# Persistência como Serviço

O Data Store deve ser tratado como um serviço institucional de persistência.

Nenhum componente da plataforma pode acessar diretamente mecanismos físicos de armazenamento.

Toda interação deve ocorrer exclusivamente através dos contratos públicos definidos pela arquitetura.

---

# Independência Tecnológica

A arquitetura do Data Store não depende de tecnologias específicas.

A infraestrutura poderá utilizar, isoladamente ou em conjunto:

- bancos relacionais;
- bancos NoSQL;
- armazenamento orientado a documentos;
- armazenamento em objetos;
- sistemas distribuídos;
- Data Lakes;
- Data Warehouses;
- mecanismos de cache;
- futuras tecnologias de persistência.

A substituição dessas tecnologias não deve provocar alterações nos componentes consumidores.

---

# Separação entre Domínio e Persistência

As regras de negócio pertencem ao domínio da aplicação.

A persistência é exclusivamente responsável por armazenar, recuperar e versionar os ativos.

O Data Store não implementa lógica de negócio, cálculos de indicadores, diagnósticos ou recomendações.

---

# Consistência Antes de Desempenho

A integridade dos dados é prioridade sobre otimizações de desempenho.

Toda operação de persistência deve preservar:

- consistência dos dados;
- integridade referencial;
- validade dos metadados;
- coerência das versões;
- rastreabilidade das alterações.

O desempenho deve ser otimizado sem comprometer esses requisitos.

---

# Versionamento Obrigatório

Todo ativo institucional possui versionamento.

Novas versões não substituem versões anteriores.

Cada versão deve possuir identidade própria, histórico completo e possibilidade de recuperação.

Esse princípio garante reprodutibilidade e auditoria.

---

# Imutabilidade das Versões Publicadas

Após a publicação, uma versão torna-se imutável.

Alterações posteriores devem resultar na criação de uma nova versão.

Esse princípio assegura estabilidade para consumidores, auditorias e processos analíticos.

---

# Lineage Nativo

Toda relação entre ativos deve ser registrada.

O Data Store deve preservar informações sobre:

- origem dos dados;
- transformações aplicadas;
- dependências;
- versões relacionadas;
- consumidores;
- artefatos gerados.

O lineage é considerado uma capacidade nativa da arquitetura.

---

# Rastreabilidade Completa

Cada operação relevante deve ser rastreável.

Isso inclui:

- criação;
- atualização;
- publicação;
- consulta;
- versionamento;
- arquivamento;
- remoção lógica.

Toda ação deve permitir reconstrução histórica.

---

# Observabilidade por Padrão

A infraestrutura deve produzir informações suficientes para monitoramento contínuo.

Devem ser disponibilizados:

- logs;
- métricas;
- eventos;
- indicadores operacionais;
- informações diagnósticas.

A observabilidade faz parte da arquitetura, não da implementação.

---

# Governança Integrada

As políticas de governança devem ser aplicadas diretamente sobre os ativos persistidos.

Entre elas:

- retenção;
- classificação;
- auditoria;
- controle de acesso;
- políticas de publicação;
- conformidade;
- ciclo de vida.

---

# Contratos Públicos Estáveis

Os consumidores interagem apenas com contratos públicos.

Mudanças internas de infraestrutura não devem impactar:

- APIs;
- modelos públicos;
- serviços;
- fluxos institucionais.

Esse princípio garante evolução contínua da plataforma.

---

# Evolução Incremental

A arquitetura deve permitir expansão sem ruptura.

Novos mecanismos de armazenamento, otimizações e funcionalidades poderão ser incorporados preservando compatibilidade com versões anteriores.

Esse princípio assegura longevidade ao Data Store e reduz riscos durante sua evolução.

---

# Próxima Seção

A próxima seção apresenta a organização estrutural da arquitetura do Data Store e seus principais componentes institucionais.