from enum import StrEnum


class QueueName(StrEnum):
    LEAD_RECEIVED = "lead.received"
    LEAD_DEAD_CONSUMER_FAILED = "lead.dead.consumer_failed"
