DELIMITER $$

CREATE PROCEDURE sp_insert_lead (
    IN p_name VARCHAR(255),
    IN p_email VARCHAR(255),
    IN p_phone VARCHAR(50),

    IN p_gateway VARCHAR(100),
    IN p_transaction_id VARCHAR(255),

    IN p_product_name VARCHAR(255),
    IN p_amount DECIMAL(10,2),

    IN p_event VARCHAR(100),

    IN p_correlation_id VARCHAR(255),
    IN p_gateway_transaction_time DATETIME,
    IN p_lag_seconds INT
)
BEGIN
    DECLARE v_lead_id BIGINT;
    DECLARE v_order_id BIGINT;

    START TRANSACTION;

    -- =========================================
    -- 1. LEAD (idempotência por email)
    -- =========================================
    SELECT id INTO v_lead_id
    FROM leads
    WHERE email = p_email
    LIMIT 1;

    IF v_lead_id IS NULL THEN

        INSERT INTO leads (name, email, phone)
        VALUES (p_name, p_email, p_phone);

        SET v_lead_id = LAST_INSERT_ID();

    END IF;

    -- =========================================
    -- 2. ORDER (idempotência por gateway + transaction_id)
    -- =========================================
    SELECT id INTO v_order_id
    FROM orders
    WHERE gateway = p_gateway
      AND transaction_id = p_transaction_id
    LIMIT 1;

    IF v_order_id IS NULL THEN

        INSERT INTO orders (
            lead_id,
            gateway,
            transaction_id,
            product_name,
            amount
        )
        VALUES (
            v_lead_id,
            p_gateway,
            p_transaction_id,
            p_product_name,
            p_amount
        );

        SET v_order_id = LAST_INSERT_ID();

    END IF;

    -- =========================================
    -- 3. LEAD EVENT (idempotência por order + event)
    -- =========================================
    INSERT INTO lead_events (
        order_id,
        correlation_id,
        event,
        gateway_transaction_time,
        persisted_at,
        lag_seconds
    )
    VALUES (
        v_order_id,
        p_correlation_id,
        p_event,
        p_gateway_transaction_time,
        NOW(),
        p_lag_seconds
    )
    ON DUPLICATE KEY UPDATE
        correlation_id = correlation_id;

    COMMIT;

    -- =========================================
    -- retorno para o worker
    -- =========================================
    SELECT
        v_lead_id AS lead_id,
        v_order_id AS order_id;

END $$

DELIMITER ;