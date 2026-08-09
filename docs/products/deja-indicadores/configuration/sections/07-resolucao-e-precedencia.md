# 07. Resolução e Precedência

## Objetivo

Esta seção descreve o mecanismo de resolução de configurações e as regras de precedência utilizadas pelo Configuration para determinar o valor final aplicado aos componentes da Deja Platform.

O objetivo é garantir que múltiplas fontes, contextos e versões possam coexistir de forma previsível e controlada.

---

# Conceito de resolução

A resolução de configuração é o processo responsável por transformar diferentes definições configuracionais em uma configuração final efetivamente aplicável.

O Configuration Resolver combina:

- definições base;
- valores específicos;
- contexto operacional;
- ambiente;
- políticas;
- versões ativas.

Resultado:

Configuration Inputs

    |

Configuration Resolver

    |

Resolved Configuration


---

# Necessidade de resolução

A Deja Platform opera em múltiplos contextos:

- desenvolvimento;
- homologação;
- produção;
- organizações diferentes;
- módulos diferentes;
- execuções específicas.

Cada contexto pode possuir necessidades configuracionais distintas.

A resolução permite flexibilidade sem duplicação de configurações.

---

# Modelo de resolução

O processo considera diferentes níveis configuracionais.

Modelo conceitual:

Default Configuration

    +

Platform Configuration

    +

Environment Configuration

    +

Module Configuration

    +

Service Configuration

    +

Runtime Override

    |

    v

Resolved Configuration


---

# Regras de precedência

A precedência define qual valor deve prevalecer quando existem múltiplas definições para a mesma configuração.

Modelo padrão:

Runtime Override

    >

Execution Context

    >

Service Configuration

    >

Module Configuration

    >

Environment Configuration

    >

Platform Configuration

    >

Default Configuration


---

# Determinismo

A resolução deve ser determinística.

Para um mesmo conjunto de:

- configuração;
- contexto;
- versão;
- políticas;

o resultado deve ser sempre o mesmo.

---

# Contexto de resolução

O Resolver utiliza informações contextuais para determinar a configuração aplicável.

Exemplos:

Resolution Context

environment

tenant

module

service

execution

user

request


---

# Valores herdados

Configurações podem utilizar herança.

Exemplo:

Platform Default

    |

Environment Override

    |

Service Override

    |

Runtime Value


A herança reduz duplicação e facilita manutenção.

---

# Sobrescritas controladas

Sobrescritas são permitidas quando:

- possuem origem identificada;
- respeitam políticas;
- possuem rastreabilidade;
- seguem precedência definida.

Nenhuma sobrescrita deve ocorrer de forma implícita.

---

# Conflitos de configuração

Quando existem conflitos, o Resolver deve:

- aplicar regras de precedência;
- validar compatibilidade;
- registrar decisão;
- informar inconsistências.

Conflitos críticos devem impedir publicação.

---

# Cache de resolução

O Configuration Runtime pode utilizar cache de configurações resolvidas.

O cache deve considerar:

- contexto;
- versão;
- validade;
- atualização.

Alterações relevantes devem invalidar valores antigos.

---

# Atualização de resolução

Quando uma configuração muda, o sistema deve permitir:

- nova resolução;
- atualização de consumidores;
- geração de eventos;
- registro de histórico.

---

# Integração com Runtime

O fluxo operacional:

Consumer Request

    |

Configuration Runtime

    |

Resolution Context

    |

Configuration Resolver

    |

Resolved Configuration

    |

Consumer


---

# Auditoria da resolução

O processo de resolução deve permitir rastrear:

- quais fontes participaram;
- qual regra prevaleceu;
- qual versão foi aplicada;
- qual contexto foi utilizado.

---

# Resultado arquitetural

O modelo de resolução e precedência garante:

- previsibilidade;
- flexibilidade;
- controle operacional;
- consistência;
- rastreabilidade.

O Configuration passa a suportar ambientes complexos sem comprometer governança.