from Utilities import ErrorMessage
################################################################################

__all__ = ("ChannelMissing",)

################################################################################
class ChannelMissing(ErrorMessage):

    def __init__(self):
        super().__init__(
            title="Channel Missing!",
            message=f"The selected channel is missing and cannot be used.",
            solution=f"Please alert a bot administrator and use another channel in the mean time.",
        )

################################################################################
        