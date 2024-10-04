from datetime import datetime
from Utilities import ErrorMessage
################################################################################
class DateBeforeNow(ErrorMessage):

    def __init__(self, invalid_value: str) -> None:

        super().__init__(
            title="Invalid Date/Time Entered",
            description=f"**Invalid Datetime Value:** `{invalid_value}`",
            message="The datetime you entered is prior to the current date and time.",
            solution=(
                "Please enter a valid date and time that is after "
                f"the current date and time ({datetime.now().strftime('%m/%d/%y %I:%M %p')})."
            )
        )

################################################################################
