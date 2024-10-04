from Utilities import ErrorMessage
################################################################################
class InvalidDate(ErrorMessage):

    def __init__(self, invalid_value: str, _fmt: str = "MM/DD/YY") -> None:

        super().__init__(
            title="Invalid Date Entered",
            description=f"**Invalid Date Value:** `{invalid_value}`",
            message="The date you entered is not in a valid format.",
            solution=f"Please enter a date in the format `{_fmt}`."
        )

################################################################################
