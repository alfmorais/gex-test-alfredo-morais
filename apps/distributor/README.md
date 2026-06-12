# Distributor Service

Este projeto é um backend em Python voltado para processamento e distribuição de eventos assíncronos, utilizando arquitetura baseada em **Domain-Driven Design (DDD)** e separação clara entre camadas de domínio, aplicação e infraestrutura.

O sistema processa mensagens de distribuição via filas (RabbitMQ), aplica regras de negócio e persiste estados e falhas para rastreabilidade.


## 🚀 Tecnologias utilizadas

- Python 3.13
- FastAPI
- Docker
- Docker Compose
- UV (gerenciador de dependências)
- SQLModel
- AsyncMy
- RabbitMQ (mensageria)
- HTTPX
- Pytest


## 📌 Requisitos

Antes de iniciar, você precisa ter instalado:

- Python 3.13+
- Docker
- Docker Compose
- UV (>= 0.11.11)


## 📦 Instalação do projeto

### 1. Instalar dependências

```bash
uv sync
```

## 🐳 Rodando com Docker

### 1. Build da imagem

```bash
docker build -t distributor .
```

## ⚙️ Rodando localmente (sem Docker)

### 1. Instalar dependências

```bash
uv sync
```

### 2. Rodar API

```bash
make run
```

## 🧪 Rodando testes

### Executar testes unitários

```bash
make unit-tests
```

Ou manualmente:

```bash
uv run pytest -vvv --cov=src --cov-report=term-missing
```

## 📁 Estrutura do projeto

O projeto segue arquitetura em camadas baseada em DDD:

```text
src/
├── application
│   ├── messages            # DTOs e modelos de mensagem
│   └── use_cases          # Casos de uso (regra de negócio principal)
│
├── domain
│   ├── entities            # Entidades de domínio
│   ├── enum                # Enums de negócio
│   ├── exceptions         # Exceções de domínio
│   ├── integrations       # Contratos de integração externa
│   ├── publishers         # Interfaces de mensageria
│   └── repositories       # Contratos de persistência
│
├── infrastructure
│   ├── database           # Implementações SQL (MySQL / SQLModel)
│   ├── integrations       # Integrações externas (HTTP, APIs)
│   ├── messaging          # RabbitMQ consumer/publisher
│   ├── log                # Logger
│
├── workers                # Workers de processamento assíncrono
├── main.py                # Entry point da aplicação
└── settings.py            # Configurações
```


## 🧠 Arquitetura

O sistema segue princípios de:

* Separação de responsabilidades (Clean Architecture / DDD)
* Independência de infraestrutura
* Uso de casos de uso para orquestração
* Domínio isolado de frameworks
* Comunicação assíncrona via RabbitMQ

Fluxo típico:

```text
RabbitMQ → Consumer → Use Case → Domain → Repository → Database
```


## 🛠️ Qualidade de código

### Lint e formatação

```bash
make check
make format
```

### Tipagem

```bash
make mypy-check
```

### Pipeline completa

```bash
make all
```

## 📄 Observações

* Projeto utiliza UV para gerenciamento rápido de dependências
* Comunicação assíncrona via RabbitMQ
* Forte separação entre domínio e infraestrutura
* Foco em escalabilidade e rastreabilidade de eventos
