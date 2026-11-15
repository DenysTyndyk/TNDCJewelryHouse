from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Protocol

from app.models.enums import Currency, PaymentProvider, PaymentStatus

class InvalidSignature(Exception):
    """Raised when a webhook cannot be proven to come from the provider."""

@dataclass(frozen=True)
class WebhookEvent:
    external_id: str
    status: Optional[PaymentStatus]
    amount: Decimal
    currency: Currency
    raw: dict

class PaymentGateway(Protocol):
    provider: PaymentProvider

    def create_checkout(self,*,external_id: str,status: Optional[PaymentStatus]
        amount: Decimal, currency: Currency, description: str,
        result_url: str,) -> str:...

    def verify_webhook(self, form: dict[str, str]) -> WebhookEvent: ...

