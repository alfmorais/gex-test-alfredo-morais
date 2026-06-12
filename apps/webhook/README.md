# Webhook Backend

Este projeto é um backend em Python voltado para processamento de eventos de webhook, utilizando uma arquitetura baseada em serviços, controllers e separação de responsabilidades por camadas.

O sistema foi construído com foco em escalabilidade, testes automatizados e execução em ambiente containerizado.

## 🚀 Tecnologias utilizadas

- Python 3.13
- FastAPI
- Docker
- Docker Compose
- UV 0.11.11 (gerenciador de dependências)
- SQLModel
- Pytest

## 📌 Requisitos

Antes de começar, você precisa ter instalado:

- Python 3.13+
- Docker
- Docker Compose
- UV 0.11.11

## 📦 Instalação do projeto

### 1. Clonar o repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd webhook
```

### 2. Instalar dependências com UV

```bash
uv sync
```

## 🐳 Rodando com Docker

### 1. Build da imagem

```bash
docker build -t webhook-api .
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

Ou diretamente:

```bash
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 9000
```

A aplicação ficará disponível em:

```
http://localhost:9000
```


## 🧪 Rodando testes

### Testes unitários

```bash
make unit-tests
```

Ou manualmente:

```bash
uv run pytest -vvv --cov=src --cov-report=term-missing
```


## 📁 Estrutura do projeto

O projeto segue uma arquitetura em camadas:

```
src/
├── controllers        # Camada de entrada (HTTP / interfaces)
├── services           # Regras de negócio e orquestração
├── models             # Entidades, repositories e database
├── views              # Rotas, schemas e enums de API
├── middlewares        # Middlewares da aplicação
├── settings.py        # Configurações gerais
├── main.py            # Entrada da aplicação FastAPI
├── lifespan.py       # Ciclo de vida da aplicação
└── logger.py         # Configuração de logs
```

Outras pastas:

```
tests/   # Testes unitários e mocks
scripts/ # Scripts auxiliares (ex: start_process.py)
```


## 🧠 Boas práticas aplicadas

* Arquitetura em camadas (controllers, services, models)
* Separação de responsabilidades
* Uso de programação assíncrona (async/await)
* Uso de tipagem forte com Python 3.13
* Testes automatizados com pytest
* Injeção de dependência via repositories e services
* Código formatado e validado com ruff + mypy


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


## 📌 Scripts úteis

### Executar processo manual

```bash
make start-process
```


## 📄 Observações

* O projeto utiliza UV como gerenciador de dependências moderno e rápido.
* Toda execução de testes e scripts deve ser feita via `uv run` para garantir isolamento do ambiente.
* A aplicação segue padrões de backend moderno com foco em escalabilidade e manutenção.
