from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.messages.lead_received_message import LeadReceivedMessage


class MySQLLeadRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def insert_lead(
        self,
        message: LeadReceivedMessage,
        lag_seconds: int,
    ) -> tuple[int, int]:
        customer = message.body.customer
        customer_name = f"{customer.first_name} {customer.last_name}"

        product = message.body.product
        payment = message.body.payment

        transaction_time = message.body.transaction_time.replace(tzinfo=None)

        result = await self._session.execute(
            text("""
                CALL sp_insert_lead(
                    :name,
                    :email,
                    :phone,
                    :gateway,
                    :transaction_id,
                    :product_name,
                    :amount,
                    :event,
                    :correlation_id,
                    :transaction_time,
                    :lag_seconds
                )
                """),
            {
                "name": customer_name,
                "email": customer.email,
                "phone": customer.phone,
                "gateway": message.gateway,
                "transaction_id": message.body.transaction_id,
                "product_name": product.name,
                "amount": payment.amount_usd,
                "event": message.body.event,
                "correlation_id": message.correlation_id,
                "transaction_time": transaction_time,
                "lag_seconds": lag_seconds,
            },
        )

        row = result.fetchone()

        if row is None:
            raise RuntimeError(
                "Stored procedure sp_insert_lead did not return a result"
            )

        response = (row.lead_id, row.order_id)
        return response
