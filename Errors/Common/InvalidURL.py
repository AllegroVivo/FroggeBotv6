from Utilities import ErrorMessage
################################################################################

__all__ = ("InvalidURL",)

################################################################################
class InvalidURL(ErrorMessage):

    def __init__(self, value: str):
        super().__init__(
            title="Invalid URL",
            description=f"Invalid Value: {value}",
            message="The URL value you entered is invalid.",
            solution="Please enter a valid URL beginning with `http://` or `https://` *(preferred)*.",
        )

################################################################################
        