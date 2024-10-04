from Utilities import ErrorMessage
################################################################################

__all__ = ("InvalidNumber",)

################################################################################
class InvalidNumber(ErrorMessage):

    def __init__(self, value: str):
        super().__init__(
            title="Invalid Number",
            description=f"Invalid Value: {value}",
            message="The numerical value you entered is invalid.",
            solution="Enter a whole number.",
        )

################################################################################
        