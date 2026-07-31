# 09. Integração com Componentes

## Objetivo

Esta seção descreve como o API Gateway integra-se com os componentes institucionais da Deja Platform.

O objetivo é definir os relacionamentos arquiteturais, responsabilidades compartilhadas e fluxos de comunicação entre o Gateway e as demais capacidades da plataforma.

---

# Visão geral

O API Gateway atua como uma capacidade transversal e depende de serviços institucionais existentes para executar suas responsabilidades.

Ele não cria mecanismos paralelos para:

- segurança;
- configuração;
- descoberta;
- execução;
- auditoria;
- observabilidade.

A integração ocorre através dos contratos públicos da própria plataforma.

---

# Integração com Kernel

O Kernel fornece os fundamentos para funcionamento do API Gateway.

Responsabilidades integradas:

- carregamento de capacidades;
- gerenciamento do ciclo de vida;
- disponibilização de serviços institucionais.

O Gateway utiliza os mecanismos do Kernel sem acoplamento direto às implementações internas.

---

# Integração com Runtime

O Runtime é responsável pelo ambiente de execução das chamadas.

A integração permite:

- criação de contexto;
- resolução de componentes;
- execução controlada;
- gerenciamento do ciclo operacional.

Fluxo conceitual:
