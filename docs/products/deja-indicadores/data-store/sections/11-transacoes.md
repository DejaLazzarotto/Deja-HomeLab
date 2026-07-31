# 11. Transações

## Objetivo

Esta seção define a arquitetura institucional de Transações do Data Store.

As transações garantem que as operações de persistência executadas pela plataforma ocorram de forma consistente, íntegra e recuperável, preservando a confiabilidade dos ativos armazenados.

---

# Conceito

Uma transação representa um conjunto de operações executadas como uma única unidade lógica de trabalho.

Todas as operações pertencentes à transação devem ser concluídas com sucesso ou integralmente revertidas.

Esse princípio assegura a integridade dos ativos persistidos.

---

# Papel do Transaction Manager

O Transaction Manager é o componente institucional responsável por coordenar o ciclo de vida das transações.

Suas principais responsabilidades incluem:

- iniciar transações;
- controlar seu estado;
- confirmar operações;
- reverter alterações quando necessário;
- registrar eventos transacionais;
- disponibilizar informações para auditoria.

A implementação física permanece independente da arquitetura.

---

# Escopo das Transações

Podem participar de uma transação operações relacionadas a:

- persistência de Datasets;
- gravação de Metadados;
- criação de Versões;
- atualização de registros de Lineage;
- persistência de Artefatos;
- gravação de Configurações;
- registros de Auditoria.

A composição da transação depende da operação executada.

---

# Estados da Transação

Toda transação percorre um ciclo de vida institucional.

Os estados previstos são:

- Created;
- Started;
- Running;
- Committed;
- Rolled Back;
- Failed.

Cada mudança de estado deve ser registrada para fins de rastreabilidade.

---

# Commit

O commit confirma definitivamente todas as operações realizadas durante a transação.

Após sua conclusão:

- os ativos tornam-se persistentes;
- os metadados permanecem consistentes;
- os registros de lineage são preservados;
- os eventos de auditoria são registrados.

Uma transação concluída não pode ser parcialmente revertida.

---

# Rollback

Caso ocorra uma falha durante a execução, a transação deve ser revertida.

O rollback deve garantir que:

- nenhum ativo incompleto permaneça persistido;
- não existam versões inconsistentes;
- o Lineage permaneça íntegro;
- a plataforma retorne ao estado anterior.

---

# Consistência

A arquitetura estabelece que toda transação deve preservar:

- integridade dos dados;
- consistência entre ativos;
- coerência das versões;
- validade dos metadados;
- integridade do Lineage.

Esses requisitos possuem prioridade sobre otimizações de desempenho.

---

# Isolamento

Transações simultâneas devem preservar isolamento lógico entre si.

A implementação poderá utilizar diferentes mecanismos para garantir esse comportamento, desde que mantenha os contratos públicos definidos pela arquitetura.

---

# Recuperação

Em caso de falhas operacionais, o Data Store deve possuir mecanismos capazes de:

- identificar transações interrompidas;
- recuperar estados consistentes;
- registrar eventos de falha;
- permitir auditoria completa da ocorrência.

As estratégias específicas pertencem à implementação.

---

# Auditoria

Cada transação deve produzir informações suficientes para identificar:

- identificador da transação;
- momento de início;
- momento de conclusão;
- operações executadas;
- ativos afetados;
- resultado final;
- responsável pela execução.

Esses registros integram a rastreabilidade institucional da plataforma.

---

# Benefícios

O modelo institucional de transações proporciona:

- consistência dos dados;
- integridade das operações;
- recuperação segura;
- confiabilidade operacional;
- auditoria completa;
- rastreabilidade das alterações;
- previsibilidade de comportamento;
- independência da tecnologia de persistência.

---

# Próxima Seção

A próxima seção apresenta a arquitetura de Integração do Data Store, definindo como a camada de persistência comunica-se com os demais componentes da Deja Indicadores por meio de contratos públicos.