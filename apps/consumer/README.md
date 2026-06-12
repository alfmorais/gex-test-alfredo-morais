# Consumer Service

Este projeto é um backend em Python voltado para consumo e processamento de eventos de leads via mensageria (RabbitMQ), utilizando arquitetura baseada em **Domain-Driven Design (DDD)** com separação clara entre domínio, aplicação e infraestrutura.

O sistema recebe mensagens de leads, valida dados, processa regras de negócio e persiste informações em banco de dados MySQL de forma assíncrona.


## 🚀 Tecnologias utilizadas

- Python 3.13
- FastAPI
- Docker
- Docker Compose
- UV (gerenciador de dependências)
- SQLModel
- AsyncMy
- RabbitMQ
- Loguru
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
docker build -t consumer .
```

## ⚙️ Rodando localmente (sem Docker)

### 1. Instalar dependências

```bash
uv sync
```

### 2. Rodar aplicação

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

O projeto segue arquitetura baseada em DDD:

```text
src/
├── application
│   ├── messages        # DTOs de entrada (mensagens de lead)
│   └── use_cases      # Casos de uso (regras de negócio)
│
├── domain
│   ├── entities        # Entidades de domínio
│   ├── enum            # Enums de negócio
│   ├── publishers      # Interfaces de mensageria
│   ├── repositories    # Contratos de persistência
│
├── infrastructure
│   ├── database        # Implementações MySQL (SQLModel)
│   ├── messaging       # RabbitMQ consumer/publisher
│   ├── log             # Logging
│
├── workers            # Workers de consumo de mensagens
├── main.py            # Entry point da aplicação
└── settings.py        # Configurações
```

## 🧠 Arquitetura

Fluxo principal do sistema:

```text
RabbitMQ → Consumer → Use Case → Domain → Repository → MySQL
```

### Responsabilidades

* **Consumer Worker**: escuta fila RabbitMQ
* **Application Layer**: orquestra casos de uso
* **Domain Layer**: regras de negócio puras
* **Infrastructure Layer**: banco, mensageria e integrações

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

* Projeto utiliza UV para gerenciamento de dependências
* Arquitetura desacoplada e orientada a eventos
* Processamento assíncrono via RabbitMQ
* Foco em escalabilidade e resiliência
