from enum import Enum


class Queues(str, Enum):
    DECRYPT_FAILED = "lead.dead.decrypt_failed"
    SCHEMA_FAILED = "lead.dead.schema_failed"
    RECEIVED = "lead.received"
