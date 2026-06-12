# Parte A: Resolução de problema real

Sendo bem honesto com o time técnico da GEX, eu nunca vivi exatamente esse tipo de cenário em um sistema corporativo de grande escala, mesmo tendo experiência com RabbitMQ em outros contextos.

Em um sistema em que trabalhei, lidávamos com cancelamentos de empréstimos de forma assíncrona usando Python e RabbitMQ, e qualquer inconsistência era controlada através de uma máquina de estados para gerenciar retries e garantir consistência eventual.

Dito isso, o plano de resposta a incidentes que descrevi aqui é mais uma construção baseada em estudo e simulações do que em experiência direta em produção nesse nível de impacto.


# 🧭 1. Primeira ação (antes de mexer em produção)

Minha primeira ação não é técnica, é de contenção e diagnóstico seguro:

### 👉 1. Confirmar impacto e congelar mudanças

* Avisar que vou investigar divergência entre gateway e pipeline interno
* Pedir para o time **não alterar nada no pipeline de eventos ou reprocessamento ainda**
* Verificar se há deploy recente no receiver/distributor

### 👉 2. Definir janela e escopo

* Confirmar:

  * período exato (sexta inteira? horário?)
  * gateway específico
  * tipo de evento (`order.approved`)
  * versão do sistema naquele dia

### 👉 3. Verificar saúde do sistema (rápido)

* RabbitMQ status
* filas acumuladas
* consumidores ativos

# 🧠 2. Hipóteses iniciais ranqueadas

## 🥇 1. Consumer travado ou parcialmente down (mais provável)

Porque:

* discrepância grande (1587 vs 421)
* sintomas incluem "call center sem leads há 4h"
* sugere pipeline interrompido

## 🥈 2. Falha no publish para fila após decrypt

Receiver pode ter recebido, mas:

* decrypt falhou silenciosamente
* evento foi dropado ou enviado para DLQ

## 🥉 3. Problema de idempotência / deduplicação excessiva

Possível:

* chave errada (ex: transaction_id + event mal aplicada)
* leads sendo ignorados como duplicados

## 4. Gateway não enviou todos os eventos

Menos provável porque:

* gateway reporta 1587
* mas isso precisa ser validado com logs externos

## 5. Falha no distribuidor downstream (após consumer)

Possível, mas não explicaria baixa contagem em `lead_events`

# 🔍 3. Dados, logs e queries iniciais

## 📊 1. Comparar ingestão por estado

```sql
SELECT event, COUNT(*)
FROM lead_events
WHERE created_at BETWEEN '2026-06-09 00:00:00' AND '2026-06-13 23:59:59'
GROUP BY event;
```

## 📊 2. Ver eventos aprovados detalhados

```sql
SELECT *
FROM lead_events
WHERE event = 'order.approved'
AND created_at >= '2026-06-09';
```

## 📊 3. Ver possíveis falhas de processamento

Se existir tabela de raw payload:

```sql
SELECT status, COUNT(*)
FROM raw_payloads
WHERE created_at >= '2026-06-09'
GROUP BY status;
```

## 🐇 RabbitMQ (ver filas críticas)

```bash
rabbitmqctl list_queues name messages consumers
```

Ou via management:

* fila `lead_events`
* fila `distributor`
* DLQ

## 🔥 Ver backlog:

```bash
rabbitmqctl list_queues name messages_ready messages_unacknowledged
```

# 🧪 4. Como diferenciar os cenários

## (a) Gateway não enviou

### sinais:

* logs do receiver não mostram volume esperado
* ausência de requests HTTP

### validação:

* logs de ingress/nginx:

```bash
grep "order.approved" nginx_access.log
```

## (b) Webhook chegou mas decrypt falhou

### sinais:

* raw_payloads existe
* mas lead_events não

### query:

```sql
SELECT *
FROM raw_payloads
WHERE event = 'order.approved'
AND status = 'decrypt_failed';
```

## (c) Consumer travou

### sinais:

* fila com mensagens acumuladas
* unack alto

```bash
rabbitmqctl list_queues name messages_ready messages_unacknowledged
```

* zero ou baixa taxa de consumo

## (d) Consumer publicou mas distribuidor falhou

### sinais:

* lead_events completo
* mas distributor queue vazia ou DLQ cheia

```sql
SELECT *
FROM distribution_status
WHERE status != 'DELIVERED';
```

# 🔁 5. Plano de reprocessamento (1.166 faltantes)

## 🧠 Princípio: idempotência total

Já temos 421 registros → não duplicar.

## 📌 Estratégia

### 1. Identificar faltantes via gateway dataset

Supondo tabela staging:

```sql
SELECT g.transaction_id
FROM gateway_events g
LEFT JOIN lead_events l
ON g.transaction_id = l.transaction_id
AND l.event = 'order.approved'
WHERE g.event = 'order.approved'
AND l.transaction_id IS NULL;
```

### 2. Publicar novamente na fila (RabbitMQ)

Reprocessamento controlado:

```python
for event in missing_events:
    channel.basic_publish(
        exchange="lead_exchange",
        routing_key="lead.approved.replay",
        body=json.dumps(event)
    )
```

### 3. Garantir idempotência no consumer

```sql
INSERT INTO lead_events (transaction_id, event)
VALUES (:transaction_id, :event)
ON CONFLICT (transaction_id, event) DO NOTHING;
```

### 4. Processar em lote controlado

* rate limit no replay
* monitorar DLQ

# 🛡️ 6. Prevenção (3 medidas fortes)

## 1. Observabilidade de gap (SLA de ingestão)

Métrica:

* gateway_count vs lead_events_count

Alerta:

```text
gap > 5% por 10 minutos → ALERTA CRÍTICO
```

## 2. DLQ + reason tracking obrigatório

Nenhum evento pode ser:

* dropado silenciosamente

Sempre:

* reason (decrypt_failed / validation_failed / duplicate)

## 3. Consumer lag monitoring (RabbitMQ)

Alertas para:

* messages_ready crescendo
* consumers = 0
* unacked alto

# 🧠 Resumo de entrevista

> Eu começaria validando impacto e congelando mudanças. Em seguida, verificaria se o problema está no ingestion layer, no decrypt ou no consumer. A hipótese mais provável é falha ou paralisação do consumer, confirmada por backlog no RabbitMQ. O reprocessamento seria feito via comparação idempotente entre gateway e sistema interno, garantindo replay seguro sem duplicação. Por fim, adicionaria métricas de gap, DLQ estruturada e monitoramento de lag para evitar recorrência.

Se quiser, posso te fazer a versão **“resposta falada de 2 minutos em entrevista sênior”** ou simular o entrevistador te interrompendo nesse cenário.
