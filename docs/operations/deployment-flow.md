# Deployment Flow — Deja Platform

## Objetivo

Este documento define o processo oficial de publicação (deploy) das aplicações da Deja Platform.

Seu objetivo é garantir que todas as aplicações sejam implantadas de forma padronizada, segura, documentada e reproduzível.

---

# Princípios

Todo deploy deve seguir os seguintes princípios:

* simplicidade;
* rastreabilidade;
* versionamento;
* possibilidade de rollback;
* mínimo tempo de indisponibilidade;
* documentação obrigatória.

Nenhuma aplicação deve ser publicada diretamente sem seguir este fluxo.

---

# Ambientes

Atualmente a plataforma possui um único ambiente de produção.

| Ambiente | Servidor        |
| -------- | --------------- |
| Produção | Node 01 — Orion |

A criação de ambientes de homologação ou desenvolvimento remoto poderá ser realizada futuramente.

---

# Fluxo de Deploy

```text
Desenvolvimento Local
        │
        ▼
Testes locais
        │
        ▼
Commit Git
        │
        ▼
Push (repositório)
        │
        ▼
Build da aplicação
        │
        ▼
Backup da versão em produção (quando aplicável)
        │
        ▼
Transferência dos arquivos para o Orion
        │
        ▼
Atualização da aplicação
        │
        ▼
Reinício do serviço (quando necessário)
        │
        ▼
Validação funcional
        │
        ▼
Deploy concluído
```

---

# Estrutura de Publicação

As aplicações são armazenadas em:

```text
/var/www/deja/apps
```

Arquivos públicos:

```text
/var/www/deja/public
```

Armazenamento persistente:

```text
/var/www/deja/storage
```

---

# Responsabilidades

## Desenvolvedor

Responsável por:

* implementar alterações;
* executar testes;
* atualizar documentação quando necessário;
* realizar commit.

---

## Plataforma

Responsável por:

* disponibilizar infraestrutura;
* proxy reverso;
* HTTPS;
* armazenamento;
* backup;
* monitoramento dos serviços.

---

# Checklist de Deploy

Antes da publicação:

* Código compilado sem erros;
* Testes executados;
* Commit realizado;
* Alterações documentadas;
* Backup realizado (quando necessário).

Após a publicação:

* Aplicação acessível;
* Logs sem erros críticos;
* Funcionalidades principais validadas;
* HTTPS funcionando;
* Proxy reverso funcionando.

---

# Rollback

Sempre que possível, o deploy deve permitir retorno rápido para a versão anterior.

O rollback poderá ser realizado por:

* restauração dos arquivos publicados;
* restauração do banco de dados (quando necessário);
* restauração das configurações do serviço.

---

# Versionamento

Toda publicação deverá estar associada a um commit Git.

Quando representar uma entrega relevante da plataforma, recomenda-se a criação de uma tag.

Exemplo:

```text
v0.1.0
v0.2.0
v1.0.0
```

---

# Serviços

Os serviços poderão ser reiniciados utilizando o mecanismo apropriado:

* systemd;
* Docker Compose;
* outros gerenciadores adotados futuramente.

O método dependerá da arquitetura de cada aplicação.

---

# Evolução

No momento, o deploy é realizado manualmente.

Como evolução da plataforma, poderão ser incorporados:

* GitHub Actions;
* CI/CD;
* deploy automatizado;
* validações automáticas;
* testes automatizados;
* publicação sem indisponibilidade (Zero Downtime Deploy).

A adoção dessas tecnologias deverá ocorrer apenas quando trouxer benefícios reais à operação da Deja Platform, preservando os princípios de simplicidade e estabilidade.
