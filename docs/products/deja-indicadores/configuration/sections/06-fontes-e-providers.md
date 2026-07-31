# 06. Fontes e Providers

## Objetivo

Esta seção descreve o modelo arquitetural das fontes de configuração e dos providers responsáveis pela integração entre o Configuration e os diferentes mecanismos de armazenamento e disponibilização de configurações.

O objetivo é permitir múltiplas origens configuracionais sem criar dependência direta entre consumidores e fontes específicas.

---

# Conceito de Configuration Source

Uma Configuration Source representa a origem onde uma configuração está armazenada ou disponibilizada.

As fontes podem possuir diferentes características:

- persistência;
- localização;
- formato;
- disponibilidade;
- nível de segurança;
- responsabilidade operacional.

---

# Tipos de fontes

A arquitetura suporta diferentes categorias de fontes.

## File Sources

Representam configurações armazenadas em arquivos.

Exemplos:

- YAML;
- JSON;
- TOML;
- arquivos de propriedades.

Uso comum:

- configurações locais;
- ambientes de desenvolvimento;
- pacotes de módulos.

---

## Environment Sources

Representam valores fornecidos pelo ambiente de execução.

Exemplos:

- variáveis de ambiente;
- parâmetros de inicialização;
- configurações do container.

Uso comum:

- deployment;
- infraestrutura;
- configuração operacional.

---

## Database Sources

Representam configurações persistidas em bancos de dados.

Uso comum:

- configurações corporativas;
- valores administrativos;
- configurações multi-tenant.

---

## Remote Sources

Representam configurações disponibilizadas por serviços externos.

Exemplos:

- APIs;
- serviços corporativos;
- plataformas de configuração distribuída.

Uso comum:

- ambientes distribuídos;
- sincronização centralizada.

---

## Secret Sources

Representam fontes especializadas para informações sensíveis.

Exemplos:

- credenciais;
- tokens;
- chaves privadas.

Devem possuir integração obrigatória com Security.

---

# Configuration Provider

O Configuration Provider é o componente responsável por abstrair o acesso às fontes.

Ele traduz diferentes mecanismos de armazenamento em uma interface comum para o Configuration.

---

# Responsabilidades do Provider

Um provider deve:

- conectar-se à fonte;
- recuperar configurações;
- converter formatos;
- normalizar dados;
- informar origem;
- reportar erros;
- respeitar políticas de acesso.

---

# Provider Contract

Todos os providers devem implementar um contrato comum.

Conceitualmente:
