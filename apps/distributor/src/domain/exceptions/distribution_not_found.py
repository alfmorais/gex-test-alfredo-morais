class DistributionNotFoundError(Exception):
    def __init__(
        self,
        order_id: int,
        channel: str,
    ) -> None:
        self.order_id = order_id
        self.channel = channel

        super().__init__(
            f"Distribution not found for "
            f"order_id={order_id} and channel={channel}"
        )
