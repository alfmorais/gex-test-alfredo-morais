# Parte B: Decisões de arquitetura

1.  Idempotência. Por que a chave natural é transaction_id + event (order + event) e não só transaction_id? O que a inclusão do event na chave permite que a chave só com transaction_id não permitiria? Em que cenário cada uma falha?

```text
Basicamente, o transaction_id corresponde a um processo de compra que pode ter vários eventos, como: aprovado, pendente de pagamento, pago, cancelado, entre outros. Dessa forma, se você processar apenas pelo transaction_id, você perde a granularidade do processamento e não consegue rastrear corretamente os diferentes eventos associados a essa transação.
```

2. Cripto. AES-256-CBC vs AES-256-GCM: qual você escolheria para um webhook novo da GEX (não-grummer)? Por quê? A quais ataques o CBC é vulnerável e o GCM não é?

```text
A diferença entre GCM e CBC é que o **GCM garante confidencialidade e integridade através de criptografia autenticada (AEAD)**. Já o CBC não possui esse recurso, sendo vulnerável a ataques como **Padding Oracle Attack**, **Bit Flipping Attack** e à **falta de garantia de integridade dos dados**.
```

3. Backpressure. Se o canal SMS começar a falhar (provedor com 90% de erro), como você protege o resto do sistema? Por que RabbitMQ + retry exponencial sozinho não basta?

```text
Eu implementaria um Circuit Breaker baseado em máquina de estados utilizando o Redis como armazenamento compartilhado, evitando que múltiplos pods precisem chamar o provedor quando ele estiver degradado.

Com isso, o sistema consegue detectar a falha do SMS provider e automaticamente “abrir o circuito”, bloqueando novas requisições e protegendo o sistema de sobrecarga e retries desnecessários.

Quando o circuito estiver aberto, as mensagens não são enviadas para o provedor e são redirecionadas para uma fila de quarentena (DLQ ou retry queue), onde poderão ser reprocessadas posteriormente de forma controlada, após a recuperação do serviço.

Dessa forma, o sistema isola o provedor problemático, evita efeito cascata de falhas e garante maior resiliência do pipeline de mensagens.
```

4. Migração entre linguagens. Cite 3 sinais que te diriam que vale migrar a parte de receiver+decrypt para outra linguagem (ex.: Python↔Go), e 3 sinais que te diriam que NÃO vale. Use o contexto da GEX descrito acima, sem responder no genérico.

```text
Quando vale a pena mudar: 
1. Alta taxa de throughput com latência sensível
2. Pressão de concorrência no ingestion layer
3. Necessidade de runtime mais previsível e resiliente

Quando NÃO vale a pena mudar:
1. O gargalo não está no receiver, mas no downstream (RabbitMQ e Banco de Dados)
2. Regras de negócio ainda estão mudando com frequência
3. Complexidade está mais em integração do que em performance

Eu acredito que o Go tem um grande potencial para mudar a forma como construímos sistemas mais escaláveis e performáticos, principalmente em workloads com alta concorrência e baixa latência.

Por outro lado, o ecossistema Python e sua comunidade madura, somados à curva de aprendizado mais suave para entregar sistemas complexos rapidamente, tornam a linguagem extremamente forte em contextos corporativos, especialmente onde a velocidade de desenvolvimento e a flexibilidade são mais importantes que otimização de runtime.
```