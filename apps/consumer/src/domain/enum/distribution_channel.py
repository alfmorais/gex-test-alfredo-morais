from enum import StrEnum


class DistributionChannel(StrEnum):
    SMS = "SMS"
    EMAIL = "EMAIL"
    CALL_CENTER = "CALL_CENTER"
    WHATSAPP = "WHATSAPP"


CHANNEL_QUEUES = {
    DistributionChannel.SMS: "dist.sms",
    DistributionChannel.EMAIL: "dist.email",
    DistributionChannel.CALL_CENTER: "dist.callcenter",
    DistributionChannel.WHATSAPP: "dist.whatsapp",
}
