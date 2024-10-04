from Utilities import ErrorMessage
################################################################################
__all__ = ("UnableToVerify",)
################################################################################
class UnableToVerify(ErrorMessage):

    def __init__(self) -> None:

        super().__init__(
            title="Unable to Verify Character",
            message="Your lodestone character was unable to be verified.",
            solution="Please ensure the character name and world are correct and try again."
        )

################################################################################
