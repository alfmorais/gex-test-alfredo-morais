from dataclasses import dataclass


@dataclass(frozen=True)
class DistributionMessage:
    order_id: int
    lead_id: int
    channel: str
    phone: str
    correlation_id: str

    @staticmethod
    def from_dict(data: dict) -> "DistributionMessage":
        return DistributionMessage(
            order_id=data["order_id"],
            lead_id=data["lead_id"],
            channel=data["channel"],
            phone=data["phone"],
            correlation_id=data["correlation_id"],
        )
