# 📌 Visão Geral do Sistema – GEX (Pipeline de Eventos e Distribuição)

## 1. Visão Geral do Fluxo

O sistema GEX é uma plataforma de processamento de leads baseada em eventos, projetada para alta escalabilidade e resiliência. O fluxo percorre três microserviços principais:

1.  **Webhook (Receiver):** Ponto de entrada que recebe payloads criptografados dos gateways (Grummer/Lous), realiza a validação inicial e publica no RabbitMQ.
2. **Arquitetura MVC com Service/Interface**: Estruturada para separar responsabilidades entre Model, View e Controller, combinada com uma camada de Service e contratos por Interface. O Controller atua apenas como ponto de entrada das requisições, delegando regras de negócio para os Services, que são abstraídos por Interfaces para garantir desacoplamento, facilitar testes unitários e permitir substituição de implementações sem impacto na camada de apresentação ou infraestrutura.
2.  **Consumer:** Processa as regras de negócio, garante a idempotência e persiste os dados no MySQL.
3.  **Distributor:** Orquestra a entrega dos leads para canais externos (SMS, Email, Call Center) com suporte a retentativas e isolamento de falhas.

## 2. Decisões arquiteturais importantes


*   **Domain-Driven Design (DDD):** Aplicado nos serviços `consumer` e `distributor` para separar a lógica de negócio (Domain) da infraestrutura (Database/Messaging), facilitando a manutenção e testes.
*   **Arquitetura Assíncrona:** O uso de RabbitMQ desacopla a ingestão da persistência e distribuição, permitindo que picos de tráfego no Gateway não derrubem o sistema de distribuição.
*   **Idempotência Granular:** Utilização da chave natural `transaction_id + event`. Isso permite que uma mesma transação passe por múltiplos estados (aprovado, pago) sem que um evento sobrescreva o outro ou seja ignorado indevidamente.
*   **Segurança com AES-256-GCM:** Escolha do modo GCM para garantir não apenas a confidencialidade, mas também a integridade dos dados (autenticação), protegendo contra ataques de bit-flipping comuns no modo CBC.

## 3. Premissas do sistema

*   **Consistência Eventual:** O sistema prioriza a disponibilidade e a partição (modelo AP do teorema CAP).
*   **At-least-once Delivery:** Mensagens podem ser reprocessadas, exigindo que todos os consumers sejam idempotentes.
*   **Isolamento de Falhas:** Problemas em um provedor de SMS não devem impactar a entrega de e-mails ou a ingestão de novos webhooks.

## 4. Índices e justificativas

*   **UNIQUE(transaction_id, event):** Essencial para a estratégia de idempotência no banco de dados, evitando duplicatas no nível de persistência.
*   **INDEX(created_at):** Necessário para consultas de reconciliação e relatórios de performance (SLA de ingestão).
*   **INDEX(status) no Distributor:** Otimiza a busca por mensagens que precisam de reprocessamento ou que falharam.

## 5. Escolha de tecnologias

*   **Python 3.13 + FastAPI:** Escolhido pela alta performance assíncrona e suporte a tipagem moderna, acelerando o desenvolvimento sem sacrificar a robustez.
*   **UV:** Gerenciador de dependências extremamente veloz que garante builds determinísticos e isolamento de ambiente.
*   **SQLModel (Pydantic + SQLAlchemy):** Unifica a definição de esquemas de API e modelos de banco de dados, reduzindo código duplicado (boilerplate).
*   **AsyncMy:** Driver assíncrono para MySQL, permitindo que os workers processem múltiplas requisições de I/O sem bloquear o loop de eventos.
*   **RabbitMQ:** Escolhido pela maturidade em gerenciar filas, DLQs e suporte nativo a confirmações de leitura (ACKs).

## 6. Resiliência e Monitoramento

*   **DLQ Estruturada:** Todas as falhas de decodificação ou validação de schema são enviadas para filas de erro com metadados sobre o motivo da falha, facilitando a depuração.
