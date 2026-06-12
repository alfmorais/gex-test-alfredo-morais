# GEX Microservices Platform

Este projeto é uma plataforma de microservices composta por diferentes aplicações Python, integradas via **RabbitMQ**, banco de dados **MySQL** e serviços auxiliares em container.

O ambiente completo é orquestrado via **Docker Compose**, permitindo subir toda a infraestrutura com um único comando.


## 🚀 Arquitetura do sistema

O sistema é composto pelos seguintes serviços:

- **webhook** → Recebe eventos externos e inicia o fluxo
- **consumer** → Consome mensagens de leads e processa regras de negócio
- **distributor** → Responsável por distribuição e orquestração de mensagens
- **mockoon** → Simula endpoints externos para testes de webhook
- **mysql** → Banco de dados principal
- **rabbitmq** → Mensageria assíncrona entre serviços


## 📌 Requisitos

Antes de rodar o projeto, você precisa ter instalado:

- Docker
- Docker Compose


## ⚙️ Como rodar o projeto

### 1. Subir toda a infraestrutura

Na raiz do projeto, execute:

```bash
docker compose up -d --build
````

### 2. Verificar serviços rodando

```bash
docker ps
```

### 3. Derrubar ambiente

```bash
docker compose down
```

## 🌐 Endpoints dos serviços

| Serviço     | URL local                                             |
| ----------- | ------------------------------------------------------|
| Webhook     | [http://localhost:9000](http://localhost:9000/docs)   |
| Consumer    |                                                       |
| Distributor |                                                       |
| Mockoon     |                                                       |
| RabbitMQ UI | [http://localhost:15672](http://localhost:15672)      |


## 🧪 Testes

Cada aplicação é independente e possui sua própria suíte de testes.

Para rodar os testes, entre na pasta do serviço desejado:

### Exemplo (Consumer)

```bash
cd apps/consumer
uv sync
make unit-tests
```

### Exemplo (Distributor)

```bash
cd apps/distributor
uv sync
make unit-tests
```

### Exemplo (Webhook)

```bash
cd apps/webhook
uv sync
make unit-tests
```


## 🗄️ Banco de dados

* MySQL roda na porta `3306`
* Database padrão: `gex`
* Scripts de inicialização ficam em:

```text
/sql
```


## 📡 Mensageria

* RabbitMQ disponível na porta `5672`
* Management UI: `http://localhost:15672`

  * user: `guest`
  * password: `guest`


## 🔧 Mock de integração externa

O serviço **Mockoon** simula APIs externas usadas pelos webhooks.

* URL base: `http://localhost:12000`
* Endpoint principal: `/webhook`


## 🧠 Observações importantes

* Toda infraestrutura é gerenciada via Docker
* Não é necessário instalar dependências Python globalmente
* Cada serviço é independente e pode ser executado separadamente
* Os testes devem ser executados dentro de cada app individual
* O sistema foi projetado para simular um ambiente distribuído real


## 📦 Subindo o projeto completo (resumo)

```bash
docker compose up -d --build
```