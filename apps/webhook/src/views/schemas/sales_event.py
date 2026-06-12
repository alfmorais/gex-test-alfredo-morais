import re

from email_validator import EmailNotValidError, validate_email
from pydantic import BaseModel, Field, computed_field, field_validator


class BaseSalesEvent(BaseModel):
    gateway: str


class BaseHeaders(BaseModel):
    content_type: str = Field(..., alias="content-type")


class EncryptedSalesEventHeaders(BaseHeaders):
    x_gr_encrypted: bool = Field(default=False, alias="X-GR-Encrypted")


class EncryptedSalesEventBody(BaseModel):
    iv: str
    ciphertext: str


class EncryptedSalesEvent(BaseModel):
    headers: EncryptedSalesEventHeaders
    body: EncryptedSalesEventBody


class Customer(BaseModel):
    first_name: str = Field(alias="first_name")
    last_name: str = Field(alias="last_name")
    email: str
    phone: str
    country: str

    @field_validator("first_name", mode="before")
    @classmethod
    def normalize_first_name(cls, value: str) -> str:
        value = (value or "").strip()
        return value or "Customer"

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("phone", mode="before")
    @classmethod
    def normalize_phone(cls, value: str) -> str:
        value = value.strip()

        if value.startswith("+"):
            return "+" + re.sub(r"\D", "", value[1:])

        return re.sub(r"\D", "", value)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def phone_valid(self) -> bool:
        digits = re.sub(r"\D", "", self.phone)
        return len(digits) >= 10

    @computed_field  # type: ignore[prop-decorator]
    @property
    def normalized_phone(self) -> str:
        digits = re.sub(r"\D", "", self.phone)

        if len(digits) >= 10:
            return f"+{digits}"

        return self.phone

    @computed_field  # type: ignore[prop-decorator]
    @property
    def email_valid(self) -> bool:
        try:
            validate_email(self.email, check_deliverability=False)
            return True
        except EmailNotValidError:
            return False


class Product(BaseModel):
    id: str
    name: str
    niche: str
    quantity: int


class Payment(BaseModel):
    status: str
    amount_usd: float = Field(alias="amount_usd")
    method: str


class Body(BaseModel):
    transaction_id: str = Field(alias="transaction_id")
    transaction_time: str = Field(alias="transaction_time")
    event: str

    customer: Customer
    product: Product
    payment: Payment

    @computed_field  # type: ignore[prop-decorator]
    @property
    def idempotency_key(self) -> str:
        return f"{self.transaction_id}:{self.event}"


class SalesEvent(BaseSalesEvent):
    headers: BaseHeaders
    body: Body
