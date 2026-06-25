# Deja Platform CLI

## Objetivo

A Deja Platform CLI é a ferramenta operacional oficial da Deja Platform.

Seu objetivo é centralizar comandos administrativos, diagnósticos e automações em um único ponto de entrada.

---

# Comando principal

A CLI será executada inicialmente a partir do repositório:

```bash
./platform/platform
```

Futuramente, poderá ser instalada globalmente como:

```bash
platform
```

---

# Subcomandos previstos

```bash
platform version
platform health
platform inventory
platform services
platform backup
platform deploy
platform restore
```

---

# Princípios

A CLI deverá seguir os princípios da plataforma:

* simplicidade;
* clareza;
* segurança;
* documentação;
* reutilização;
* evolução incremental.

---

# Estrutura

```text
platform/
├── platform
├── lib
│   ├── common.sh
│   ├── colors.sh
│   ├── logger.sh
│   └── output.sh
│
├── commands
│   ├── version.sh
│   ├── health.sh
│   ├── inventory.sh
│   ├── services.sh
│   ├── backup.sh
│   ├── deploy.sh
│   └── restore.sh
│
└── config
    └── platform.conf
```

---

# Primeiro objetivo

A primeira versão da CLI deverá implementar:

```bash
./platform/platform version
```

Esse comando deverá exibir:

* nome da plataforma;
* versão;
* node principal;
* hostname esperado;
* ambiente atual.

---

# Evolução

A CLI será expandida gradualmente.

Nenhum comando complexo deverá ser criado antes de existir:

* documentação;
* objetivo claro;
* comportamento esperado;
* teste manual validado.
