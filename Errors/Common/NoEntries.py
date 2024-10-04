from Utilities import ErrorMessage
################################################################################
__all__ = ("NoEntries",)
################################################################################
class NoEntries(ErrorMessage):

    def __init__(self, activity: str) -> None:

        super().__init__(
            title=f"No {activity.title()} Entries Found",
            message=f"There are no entries for this {activity.lower()}.",
            solution=f"You may not roll a {activity.lower()} without any entries."
        )

################################################################################
