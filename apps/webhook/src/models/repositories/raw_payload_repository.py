from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.entities.raw_payload import RawPayload


class RawPayloadRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, raw_payload: RawPayload) -> bool:
        try:
            self.session.add(raw_payload)
            await self.session.commit()
            return True

        except IntegrityError:
            await self.session.rollback()
            return False

    async def exists(self, idempotency_key: str) -> bool:
        statement = (
            select(RawPayload)
            .where(RawPayload.idempotency_key == idempotency_key)  # type: ignore[arg-type]
            .limit(1)
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none() is not None
