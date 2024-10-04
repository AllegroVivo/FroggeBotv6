from Utilities import ErrorMessage
################################################################################

__all__ = ("InvalidMonetaryAmount",)

################################################################################
class InvalidMonetaryAmount(ErrorMessage):

    def __init__(self, value: str):
        super().__init__(
            title="Invalid Monetary Amount",
            description=f"Invalid Value: {value}",
            message="The monetary amount you entered is invalid.",
            solution=(
                "Enter __**only**__ a whole number, with or without the commas. "
                "(You may use 'k' or 'm' to represent thousands or millions.)"
            ),
        )

################################################################################
        