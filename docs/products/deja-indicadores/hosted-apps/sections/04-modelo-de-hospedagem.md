# 04. Modelo de Hospedagem

## Visão Geral

A Hosted Apps estabelece o modelo institucional de hospedagem das aplicações executadas na Deja Platform.

Esse modelo define como aplicações são registradas, implantadas, configuradas, executadas, monitoradas e administradas ao longo de todo o seu ciclo de vida.

A hospedagem é totalmente desacoplada da lógica de negócio das aplicações, oferecendo uma infraestrutura comum, segura e escalável para qualquer tipo de aplicação suportada pela plataforma.

---

## Modelo Institucional

Toda aplicação hospedada é tratada como um ativo institucional da plataforma.

Cada aplicação possui identidade própria, metadados, configuração, versões, ambiente de execução e políticas operacionais administradas pela Hosted Apps.

O modelo é uniforme para todas as aplicações, independentemente de sua origem.

---

## Categorias de Aplicações

A arquitetura suporta diferentes categorias de aplicações hospedadas:

- aplicações institucionais
- aplicações comerciais
- aplicações de clientes
- aplicações de parceiros
- aplicações de terceiros homologadas
- aplicações experimentais autorizadas

Todas seguem o mesmo modelo arquitetural de hospedagem.

---

## Estrutura de Hospedagem

Cada aplicação hospedada é composta pelos seguintes elementos institucionais:

- Identificador da aplicação
- Manifesto da aplicação
- Metadados
- Versões
- Configurações
- Recursos necessários
- Ambiente de execução
- Estado operacional
- Políticas de segurança
- Informações de observabilidade

Esses elementos permitem gerenciamento completo da aplicação durante toda sua existência.

---

## Ambientes de Execução

A Hosted Apps suporta múltiplos ambientes de execução, incluindo:

- desenvolvimento
- homologação
- produção
- ambientes privados
- ambientes dedicados por tenant

Cada ambiente possui configurações, recursos e políticas próprias.

---

## Independência das Aplicações

Cada aplicação permanece completamente independente das demais.

A arquitetura garante:

- implantação independente
- atualização independente
- rollback independente
- escalabilidade independente
- monitoramento independente
- gerenciamento independente

Essa independência reduz impactos operacionais e facilita a evolução contínua.

---

## Integração com a Plataforma

Aplicações hospedadas utilizam exclusivamente os contratos públicos disponibilizados pelas capacidades institucionais da Deja Platform.

Não é permitido acesso direto a componentes internos de outras capacidades.

Toda integração ocorre por meio de APIs, eventos, serviços ou contratos oficiais.

---

## Escalabilidade

O modelo de hospedagem foi concebido para suportar crescimento contínuo.

Entre as capacidades previstas estão:

- múltiplas instâncias
- balanceamento de carga
- expansão horizontal
- distribuição por ambientes
- atualização sem interrupção
- recuperação automática

---

## Administração Operacional

Toda administração das aplicações hospedadas é realizada pelas capacidades institucionais de administração da plataforma.

A Hosted Apps fornece os mecanismos necessários para:

- registrar aplicações
- implantar versões
- iniciar execução
- interromper execução
- atualizar aplicações
- remover aplicações
- consultar estado operacional
- acompanhar disponibilidade

---

## Compatibilidade Evolutiva

O modelo de hospedagem foi definido para permitir evolução tecnológica sem alterar os contratos institucionais da plataforma.

Novas tecnologias de execução poderão ser incorporadas mantendo compatibilidade com aplicações já hospedadas e preservando a estabilidade da arquitetura da Deja Platform.