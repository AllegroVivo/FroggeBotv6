from Utilities import ErrorMessage
################################################################################

__all__ = ("ChannelNotSet",)

################################################################################
class ChannelNotSet(ErrorMessage):

    def __init__(self, channel: str):
        super().__init__(
            title="Channel Not Set",
            message=f"The `{channel}` channel has not been set.",
            solution=f"Please set the `{channel}` channel before attempting to use this command.",
        )

################################################################################
        