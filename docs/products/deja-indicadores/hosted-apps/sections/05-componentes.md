# 05. Componentes

## Visão Geral

A Hosted Apps é composta por um conjunto de componentes institucionais especializados que, em conjunto, fornecem toda a infraestrutura necessária para hospedagem, implantação, execução, gerenciamento e monitoramento das aplicações da Deja Platform.

Cada componente possui responsabilidades bem definidas e comunica-se exclusivamente através de contratos públicos.

---

## Application Registry

Responsável pelo cadastro institucional das aplicações hospedadas.

Suas responsabilidades incluem:

- registro de aplicações
- identificação única
- metadados
- proprietário
- classificação
- versões disponíveis
- ambiente padrão
- estado administrativo

Não executa operações de deployment ou execução.

---

## Application Catalog

Mantém o catálogo institucional das aplicações disponíveis para hospedagem.

Gerencia:

- aplicações registradas
- versões homologadas
- categorias
- compatibilidade
- dependências
- histórico de versões

O catálogo constitui a referência oficial das aplicações suportadas.

---

## Deployment Manager

Responsável pelo gerenciamento institucional de implantação das aplicações.

Entre suas funções:

- instalação
- atualização
- rollback
- remoção
- validação de deployment
- distribuição por ambientes

Todas as operações seguem políticas definidas pela Governança.

---

## Lifecycle Manager

Controla o ciclo de vida completo das aplicações.

Gerencia estados como:

- registrada
- instalada
- configurada
- iniciada
- suspensa
- atualizada
- desativada
- removida

Todas as transições são auditáveis.

---

## Runtime Manager

Responsável pela execução operacional das aplicações.

Suporta:

- inicialização
- parada
- reinicialização
- monitoramento
- recuperação
- gerenciamento de instâncias

Não implementa lógica de negócio.

---

## Isolation Manager

Garante isolamento entre:

- organizações
- tenants
- ambientes
- aplicações
- configurações
- recursos computacionais

Esse componente constitui um dos pilares da arquitetura.

---

## Configuration Integration

Integra a Hosted Apps à capacidade Configuration.

Permite que aplicações obtenham configurações por meio dos contratos públicos da plataforma, respeitando escopo, precedência e contexto de execução.

---

## Security Integration

Integra todas as operações da Hosted Apps à capacidade Security.

Inclui:

- autenticação
- autorização
- credenciais
- políticas de acesso
- auditoria
- gerenciamento de segredos

Nenhuma política de segurança é implementada localmente.

---

## Observability Integration

Encaminha informações operacionais para a capacidade Observability.

Inclui:

- logs
- métricas
- eventos
- traces
- indicadores de disponibilidade
- informações de execução

Toda telemetria utiliza contratos institucionais.

---

## Administration Integration

Disponibiliza as funcionalidades administrativas da Hosted Apps para:

- Administration Platform
- Administration Console

Essas capacidades realizam toda a administração operacional utilizando exclusivamente os contratos públicos disponibilizados pela Hosted Apps.

---

## Relação entre Componentes

Os componentes atuam de forma coordenada durante todo o ciclo de vida das aplicações hospedadas.

Cada componente mantém responsabilidade exclusiva sobre seu domínio, reduzindo acoplamento, facilitando evolução independente e preservando a estabilidade arquitetural da Deja Platform.