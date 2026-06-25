# Application Workspace

## Objetivo

O **Application Workspace** define a estrutura padrão utilizada para armazenar, organizar e manter todas as aplicações hospedadas na Deja Platform.

Seu objetivo é garantir consistência, facilitar a manutenção, simplificar o deploy e permitir o crescimento da plataforma sem perda de organização.

---

# Localização

O Application Workspace está localizado em:

```text
/var/www/deja
```

Todo sistema publicado na plataforma deverá estar contido neste Workspace ou em uma estrutura oficialmente documentada.

---

# Estrutura Atual

Atualmente o Workspace encontra-se organizado da seguinte forma:

```text
/var/www/deja
│
├── apps
├── public
└── storage
```

---

# Responsabilidades

O Workspace é responsável por:

* armazenar aplicações web;
* disponibilizar conteúdo ao NGINX;
* centralizar projetos publicados;
* separar código de dados persistentes;
* manter uma organização padronizada.

---

# Organização dos Diretórios

## apps

Contém as aplicações da plataforma.

Exemplos:

* Portal
* Album Admin
* Album Mobile
* BioQuest
* Financeiro
* Sistema de Chamados

Cada aplicação deve possuir seu próprio diretório.

Não é permitido compartilhar arquivos entre aplicações.

---

## public

Destinado a recursos públicos compartilhados entre aplicações.

Exemplos:

* arquivos estáticos;
* downloads públicos;
* imagens compartilhadas;
* favicon;
* recursos institucionais.

---

## storage

Destinado ao armazenamento persistente.

Exemplos:

* uploads;
* mídias;
* arquivos enviados por usuários;
* conteúdo gerado pelas aplicações.

Nenhum arquivo de código-fonte deverá ser armazenado neste diretório.

---

# Organização das Aplicações

Cada aplicação deverá possuir um diretório exclusivo.

Exemplo:

```text
apps/
├── portal
├── album-admin
├── album-mobile
├── bioquest-pwa
├── financeiro-pwa
└── chamados-pwa
```

Cada projeto deverá ser independente dos demais.

---

# Convenções

As aplicações deverão seguir os seguintes padrões:

* nomes em letras minúsculas;
* palavras separadas por hífen (`kebab-case`);
* um projeto por diretório;
* sem compartilhamento de código entre aplicações publicadas;
* configuração independente.

---

# Evolução Planejada

À medida que a plataforma evoluir, poderá ser criada uma separação entre aplicações e serviços.

Estrutura prevista:

```text
/var/www/deja
│
├── apps
├── services
├── public
└── storage
```

Os serviços compartilhados (APIs, autenticação, mensageria, etc.) passarão a residir no diretório `services`.

Essa alteração será realizada apenas quando houver necessidade técnica.

---

# Boas Práticas

Toda nova aplicação deverá:

* possuir documentação própria;
* possuir estratégia de deploy documentada;
* possuir estratégia de backup quando aplicável;
* utilizar controle de versão;
* seguir os padrões definidos pela Deja Platform.

---

# Relação com a Arquitetura

O Application Workspace pertence ao domínio **Applications** da Deja Platform.

Ele representa a camada responsável pela publicação e organização das aplicações disponibilizadas aos usuários.

Sua estrutura é independente da infraestrutura física, permitindo que a plataforma evolua sem alterar os princípios arquiteturais estabelecidos.
