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
.
├── Dockerfile
├── Makefile
├── README.md
├── pyproject.toml
├── scripts
│   ├── __init__.py
│   └── start_process.py
├── src
│   ├── __init__.py
│   ├── controllers
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-313.pyc
│   │   │   └── event_sales_controller.cpython-313.pyc
│   │   ├── event_sales_controller.py
│   │   ├── interfaces
│   │   │   ├── __init__.py
│   │   │   └── event_sales_interface.py
│   │   └── services
│   │       ├── __init__.py
│   │       └── event_sales
│   │           ├── __init__.py
│   │           ├── __pycache__
│   │           │   ├── __init__.cpython-313.pyc
│   │           │   ├── base_service.cpython-313.pyc
│   │           │   ├── grummer_service.cpython-313.pyc
│   │           │   └── lous_service.cpython-313.pyc
│   │           ├── base_service.py
│   │           ├── grummer_service.py
│   │           └── lous_service.py
│   ├── lifespan.py
│   ├── logger.py
│   ├── main.py
│   ├── middlewares.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── database
│   │   │   ├── __init__.py
│   │   │   └── config.py
│   │   ├── entities
│   │   │   ├── __init__.py
│   │   │   └── raw_payload.py
│   │   ├── queue
│   │   │   ├── __init__.py
│   │   │   └── publisher_event.py
│   │   └── repositories
│   │       ├── __init__.py
│   │       └── raw_payload_repository.py
│   ├── settings.py
│   └── views
│       ├── __init__.py
│       ├── enum
│       │   ├── __init__.py
│       │   ├── gateways.py
│       │   └── queues.py
│       ├── routers
│       │   ├── __init__.py
│       │   └── webhook.py
│       └── schemas
│           ├── __init__.py
│           ├── sales_event.py
│           └── sales_event_context.py
├── tests
│   ├── __init__.py
│   ├── __pycache__
│   │   └── __init__.cpython-313.pyc
│   ├── controllers
│   │   ├── __init__.py
│   │   ├── services
│   │   │   ├── __init__.py
│   │   │   └── event_sales
│   │   │       ├── __init__.py
│   │   │       ├── test_base_service.py
│   │   │       ├── test_grummer_service.py
│   │   │       └── test_lous_service.py
│   │   └── test_event_sales_controller.py
│   ├── mock
│   │   └── webhook_payloads.json
│   ├── models
│   │   ├── __init__.py
│   │   ├── queues
│   │   │   ├── __init__.py
│   │   │   └── test_publisher_event.py
│   │   └── repositories
│   │       ├── __init__.py
│   │       └── test_raw_payload_repository.py
│   └── views
│       ├── __init__.py
│       ├── enum
│       │   ├── __init__.py
│       │   ├── test_gateways.py
│       │   └── test_queues.py
│       ├── routers
│       │   ├── __init__.py
│       │   └── test_webhook.py
│       └── schemas
│           ├── __init__.py
│           ├── test_sales_event.py
│           └── test_sales_event_context.py
└── uv.lock
53 directories, 125 files
```

# Estrutura de Pastas

## `/scripts`

Contém scripts auxiliares utilizados para execução de tarefas operacionais da aplicação, como inicialização de processos, jobs agendados, migrações ou rotinas de manutenção. O arquivo `start_process.py` é responsável por iniciar o fluxo principal de processamento da aplicação.

## `/src`

Diretório principal do código-fonte da aplicação, organizado seguindo uma arquitetura baseada em MVC (Model-View-Controller) complementada por camadas de Service e Interface para promover desacoplamento e facilitar testes.

### `/src/controllers`

Camada responsável por orquestrar o fluxo da aplicação. Os controllers recebem os dados provenientes das rotas, aplicam regras de validação e delegam o processamento para os serviços apropriados.

#### `/src/controllers/interfaces`

Define contratos (interfaces) utilizados pelos controllers. Essas abstrações permitem desacoplamento entre as implementações concretas e as camadas consumidoras.

#### `/src/controllers/services`

Contém os serviços responsáveis pela implementação das regras de negócio da aplicação.

##### `/src/controllers/services/event_sales`

Agrupa os serviços relacionados ao processamento de eventos de vendas. Cada serviço possui uma responsabilidade específica dentro do fluxo de tratamento dos eventos recebidos.

### `/src/models`

Camada responsável pela representação e persistência dos dados da aplicação.

#### `/src/models/database`

Contém configurações de conexão e acesso ao banco de dados.

#### `/src/models/entities`

Define as entidades de domínio utilizadas pela aplicação, representando estruturas de dados manipuladas pelas regras de negócio.

#### `/src/models/queue`

Responsável pela integração com sistemas de mensageria, incluindo publicação de eventos e comunicação assíncrona entre serviços.

#### `/src/models/repositories`

Implementa o padrão Repository, encapsulando operações de acesso aos dados e isolando detalhes de persistência das demais camadas da aplicação.

### `/src/views`

Camada responsável pela exposição da aplicação para consumidores externos, incluindo rotas, contratos de entrada e saída e definições de integração.

#### `/src/views/routers`

Define os endpoints da aplicação e o roteamento das requisições HTTP.

#### `/src/views/schemas`

Contém os modelos de validação e serialização de dados utilizados nas requisições e respostas da API.

#### `/src/views/enum`

Centraliza enums e constantes compartilhadas entre as camadas da aplicação, como filas, gateways e tipos de integração.

### Arquivos de Infraestrutura

#### `main.py`

Ponto de entrada da aplicação. Responsável pela inicialização do servidor, registro das rotas e configuração dos componentes necessários para execução.

#### `lifespan.py`

Gerencia o ciclo de vida da aplicação, executando processos de inicialização e encerramento de recursos compartilhados.

#### `middlewares.py`

Contém middlewares responsáveis por interceptar requisições e respostas para tratamento de autenticação, logging, observabilidade e outras funcionalidades transversais.

#### `settings.py`

Centraliza as configurações da aplicação, incluindo variáveis de ambiente, parâmetros de infraestrutura e configurações externas.

#### `logger.py`

Configura o sistema de logs da aplicação, padronizando o registro de eventos, erros e informações operacionais.

## `/tests`

Contém os testes automatizados da aplicação organizados seguindo a mesma estrutura do código-fonte.

### `/tests/controllers`

Testes unitários e de integração relacionados aos controllers e serviços da camada de negócio.

### `/tests/models`

Testes das camadas de persistência, repositórios e integração com filas de mensagens.

### `/tests/views`

Testes das rotas, schemas e componentes responsáveis pela exposição da API.

### `/tests/mock`

Arquivos de apoio utilizados durante os testes, como payloads simulados e dados fictícios.

## Arquivos de Configuração

### `Dockerfile`

Define a imagem Docker utilizada para empacotar e executar a aplicação em ambientes padronizados.

### `Makefile`

Centraliza comandos operacionais e de desenvolvimento, simplificando tarefas recorrentes como execução de testes, lint, build e deploy.

### `pyproject.toml`

Arquivo de configuração do projeto Python, contendo dependências, ferramentas de desenvolvimento e parâmetros de build.

### `uv.lock`

Arquivo de lock de dependências, garantindo reprodutibilidade do ambiente entre diferentes execuções e ambientes.

### `README.md`

Documentação principal do projeto contendo instruções de instalação, execução, arquitetura e utilização da aplicação.



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
