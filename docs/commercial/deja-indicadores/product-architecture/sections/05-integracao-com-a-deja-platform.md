# Integração com a Deja Platform

## Objetivo

Este documento define a relação institucional entre a Deja Indicadores e a Deja Platform.

Seu objetivo é estabelecer quais responsabilidades pertencem à plataforma, quais pertencem ao produto e como ocorre a integração entre essas duas camadas.

Essa separação é fundamental para preservar a reutilização das capacidades da plataforma e garantir a evolução independente dos produtos construídos sobre ela.

---

# Visão Geral

A Deja Platform é uma plataforma de desenvolvimento de aplicações modulares.

A Deja Indicadores é um produto comercial construído utilizando as capacidades disponibilizadas por essa plataforma.

Essa relação pode ser resumida da seguinte forma:

> A plataforma fornece capacidades técnicas.

> O produto utiliza essas capacidades para entregar valor de negócio.

A plataforma não possui conhecimento da metodologia Deja Indicadores.

Da mesma forma, o produto não implementa infraestrutura reutilizável.

---

# Responsabilidades da Deja Platform

A Deja Platform é responsável por disponibilizar capacidades institucionais reutilizáveis.

Entre elas destacam-se:

- autenticação;
- autorização;
- gerenciamento de usuários;
- gerenciamento de módulos;
- ciclo de vida dos módulos;
- Workspace SDK;
- dashboards;
- widgets;
- infraestrutura de renderização;
- infraestrutura de comandos;
- infraestrutura de eventos;
- infraestrutura de ações;
- infraestrutura de extensões;
- persistência compartilhada;
- configuração institucional;
- observabilidade;
- APIs compartilhadas;
- infraestrutura de integração;
- gerenciamento de recursos;
- runtime da plataforma.

Essas capacidades podem ser utilizadas por qualquer produto desenvolvido sobre a Deja Platform.

---

# Responsabilidades da Deja Indicadores

A Deja Indicadores é responsável exclusivamente pelo domínio de negócio da metodologia.

Entre suas responsabilidades encontram-se:

- empresas;
- indicadores;
- metas;
- diagnósticos;
- planos de ação;
- avaliações;
- acompanhamento;
- metodologia de gestão;
- jornadas do cliente;
- regras comerciais;
- relatórios especializados.

Nenhuma dessas responsabilidades deverá ser promovida para a plataforma.

---

# Critério para Promoção de Capacidades

Sempre que surgir uma nova necessidade durante a evolução do produto, deverá ser respondida a seguinte pergunta:

> Esta capacidade pode ser reutilizada por outros produtos da Deja Platform?

Se a resposta for **sim**, a implementação deverá ocorrer na Deja Platform.

Se a resposta for **não**, a implementação permanecerá na Deja Indicadores.

Esse critério evita duplicação de infraestrutura e preserva a independência entre plataforma e produto.

---

# Contratos de Integração

Toda integração entre produto e plataforma deverá ocorrer por contratos institucionais.

Exemplos:

- APIs públicas;
- interfaces;
- serviços publicados;
- eventos;
- comandos;
- pontos de extensão;
- contratos de persistência.

O acesso direto às implementações internas da plataforma não é permitido.

---

# Fluxo de Integração

A interação entre produto e plataforma ocorre conforme o fluxo abaixo.

```text
Usuário
    │
    ▼
Deja Indicadores
    │
    ▼
APIs Institucionais
    │
    ▼
Capacidades da Deja Platform
    │
    ▼
Workspace SDK
    │
    ▼
Platform Kernel
```

Cada camada conhece apenas os contratos publicados pela camada imediatamente inferior.

Essa organização reduz acoplamento e aumenta a previsibilidade da evolução arquitetural.

---

# Evolução Compartilhada

A evolução da Deja Platform e da Deja Indicadores ocorre de forma coordenada, porém independente.

Novas capacidades podem surgir em qualquer uma das camadas.

Quando uma capacidade originalmente desenvolvida no produto demonstrar potencial de reutilização por outros produtos, ela poderá ser promovida para a plataforma.

Após essa promoção, o produto passa a consumir a capacidade disponibilizada pela plataforma.

Esse processo fortalece continuamente o ecossistema da Deja Platform.

---

# Benefícios da Separação

A definição clara de responsabilidades proporciona diversos benefícios:

- maior reutilização de infraestrutura;
- menor duplicação de código;
- baixo acoplamento;
- evolução independente;
- manutenção simplificada;
- maior estabilidade arquitetural;
- facilidade para criação de novos produtos;
- fortalecimento contínuo da Deja Platform.

---

# Processo de Evolução

Toda nova funcionalidade deverá seguir o seguinte fluxo de decisão arquitetural:

```text
Nova Necessidade
        │
        ▼
É reutilizável?
        │
   ┌────┴────┐
   │         │
  Sim       Não
   │         │
   ▼         ▼
Deja      Deja
Platform Indicadores
```

Esse processo deverá orientar todas as decisões de arquitetura durante a evolução da solução.

---

# Considerações Finais

A integração entre a Deja Indicadores e a Deja Platform é baseada na separação explícita entre infraestrutura e negócio.

Essa abordagem garante que a plataforma evolua como um conjunto de capacidades institucionais reutilizáveis, enquanto a Deja Indicadores permanece focada exclusivamente na entrega de valor ao cliente por meio de sua metodologia de gestão.

Esse modelo constitui um dos pilares arquiteturais da Deja Platform e deverá ser observado por todos os produtos desenvolvidos sobre ela.