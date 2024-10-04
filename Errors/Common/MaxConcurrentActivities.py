from Utilities import ErrorMessage
################################################################################
__all__ = ("MaxConcurrentActivities",)
################################################################################
class MaxConcurrentActivities(ErrorMessage):

    def __init__(self, activity: str, max_amt: int) -> None:

        super().__init__(
            title=f"Max Concurrent {activity.title()}s Reached",
            description=f"**Maximum Concurrent {activity.title()}s:** `{max_amt}`",
            message=f"You cannot create any more active {activity.lower()}s.",
            solution=(
                f"You can wait for one of the current {activity.lower()}s to end or "
                f"deactivate one of the current {activity.lower()}s."
            )
        )

################################################################################
