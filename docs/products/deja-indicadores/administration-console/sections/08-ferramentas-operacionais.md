# 08. Ferramentas Operacionais

## Objetivo

Definir a arquitetura das ferramentas operacionais disponibilizadas pela Administration Console para apoiar a administração diária da Deja Platform, oferecendo recursos padronizados que aumentem a produtividade, reduzam erros operacionais e proporcionem uma experiência administrativa consistente.

---

## Papel das Ferramentas Operacionais

As ferramentas operacionais complementam os consoles administrativos especializados.

Seu objetivo é oferecer mecanismos comuns reutilizáveis para execução de atividades administrativas, sem incorporar regras de negócio próprias.

Toda operação executada pelas ferramentas é encaminhada às capacidades institucionais responsáveis por meio de contratos públicos.

---

## Categorias de Ferramentas

A arquitetura contempla diferentes categorias de ferramentas operacionais.

### Pesquisa Global

Permite localizar rapidamente:

- organizações;
- tenants;
- usuários;
- módulos;
- recursos administrativos;
- configurações;
- registros.

---

### Ações Rápidas

Disponibiliza atalhos para operações frequentemente utilizadas, como:

- criação de organizações;
- criação de tenants;
- administração de usuários;
- abertura de diagnósticos;
- acesso a configurações;
- consulta de eventos;
- execução de assistentes.

---

### Assistentes Administrativos

Fluxos guiados para operações complexas.

Exemplos:

- criação de ambientes;
- configuração inicial;
- onboarding administrativo;
- instalação de módulos;
- migrações;
- parametrizações.

---

### Ferramentas de Diagnóstico

Disponibilizam recursos para análise operacional da plataforma, incluindo:

- verificação de integridade;
- validação de configurações;
- análise de conectividade;
- consulta de eventos;
- inspeção de serviços;
- diagnóstico de dependências.

---

### Exportação e Importação

Permitem interoperabilidade administrativa por meio de:

- exportação de dados;
- importação controlada;
- backups administrativos;
- restauração de configurações;
- compartilhamento de artefatos.

---

### Centro de Notificações

Consolida eventos administrativos provenientes das capacidades institucionais.

Inclui:

- alertas;
- avisos;
- mensagens operacionais;
- eventos importantes;
- tarefas pendentes.

---

## Integração Institucional

As ferramentas operacionais utilizam exclusivamente APIs públicas disponibilizadas pelas capacidades institucionais.

Nenhuma ferramenta possui acesso direto às implementações internas da plataforma.

---

## Extensibilidade

Novas ferramentas podem ser adicionadas dinamicamente por futuras capacidades institucionais, preservando a arquitetura modular da Administration Console.

---

## Benefícios

A arquitetura das ferramentas operacionais proporciona:

- reutilização;
- consistência operacional;
- redução da complexidade;
- produtividade administrativa;
- baixo acoplamento;
- evolução incremental;
- integração institucional padronizada.