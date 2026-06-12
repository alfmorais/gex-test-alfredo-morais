CREATE TABLE IF NOT EXISTS raw_payloads (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    transaction_id VARCHAR(255),
    event VARCHAR(255),

    idempotency_key VARCHAR(255) NULL,
    correlation_id VARCHAR(255) NOT NULL,
    gateway VARCHAR(100) NOT NULL,

    received_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    headers JSON NOT NULL,
    body JSON NOT NULL,
    decrypted_body JSON NULL,
    raw_payload JSON NOT NULL,

    CONSTRAINT uq_idempotency_key
        UNIQUE (idempotency_key),

    CONSTRAINT uq_transaction_event
        UNIQUE (transaction_id, event),

    INDEX idx_idempotency_key (idempotency_key)
);


CREATE TABLE leads (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT uk_leads_email
        UNIQUE (email)
);


CREATE TABLE orders (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    lead_id BIGINT NOT NULL,

    gateway VARCHAR(100) NOT NULL,
    transaction_id VARCHAR(255) NOT NULL,

    product_name VARCHAR(255),
    amount DECIMAL(10,2),

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_orders_lead
        FOREIGN KEY (lead_id)
        REFERENCES leads(id),

    CONSTRAINT uk_gateway_transaction
        UNIQUE (gateway, transaction_id),

    INDEX idx_orders_lead_id (lead_id)
);


CREATE TABLE lead_events (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    order_id BIGINT NOT NULL,

    correlation_id VARCHAR(255) NOT NULL,

    event VARCHAR(100) NOT NULL,

    gateway_transaction_time DATETIME NOT NULL,

    persisted_at DATETIME NOT NULL,

    lag_seconds INT NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_lead_events_order
        FOREIGN KEY (order_id)
        REFERENCES orders(id),

    CONSTRAINT uk_order_event
        UNIQUE (order_id, event),

    INDEX idx_lead_events_transaction_time (
        gateway_transaction_time
    ),

    INDEX idx_lead_events_correlation (
        correlation_id
    )
);


CREATE TABLE distribution_status (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    order_id BIGINT NOT NULL,

    channel ENUM(
        'SMS',
        'EMAIL',
        'CALL_CENTER',
        'WHATSAPP'
    ) NOT NULL,

    status ENUM(
        'PENDING',
        'PROCESSING',
        'DELIVERED',
        'FAILED'
    ) NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NULL,

    delivered_at TIMESTAMP NULL,

    lag_seconds INT NULL,

    CONSTRAINT fk_distribution_order
        FOREIGN KEY (order_id)
        REFERENCES orders(id),

    INDEX idx_distribution_channel_status (
        channel,
        status
    ),

    INDEX idx_distribution_delivered (
        delivered_at
    ),

    INDEX idx_distribution_order (
        order_id
    )
);


CREATE TABLE lead_dead_letter (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    source_queue VARCHAR(255) NOT NULL,

    payload JSON NOT NULL,

    error_message TEXT NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_dlq_created_at (
        created_at
    ),

    INDEX idx_dlq_source_queue (
        source_queue
    )
);