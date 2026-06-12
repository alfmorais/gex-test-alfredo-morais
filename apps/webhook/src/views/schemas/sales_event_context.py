from dataclasses import dataclass, field
from typing import Any

from src.views.schemas.sales_event import SalesEvent


@dataclass
class SalesEventContext:
    correlation_id: str

    gateway: str
    headers: dict
    original_body: dict
    validated_body: SalesEvent | None = None

    decrypted_body: dict | None = None

    schema_valid: bool = False
    decrypt_failed: bool = False
    duplicate: bool = False

    validation_errors: list[Any] = field(default_factory=list)
