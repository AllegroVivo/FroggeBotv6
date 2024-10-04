from Utilities.ErrorMessage import ErrorMessage
################################################################################
__all__ = ("MaxItemsReached",)
################################################################################
class MaxItemsReached(ErrorMessage):

    def __init__(self, item_type: str, max_qty: int) -> None:

        super().__init__(
            title=f"Max {item_type.title()}s Reached",
            description=f"**Maximum Allowed {item_type.title()}s** `{max_qty}`",
            message=(
                f"You have reached the maximum allowed number of "
                f"{item_type.lower()}s for this server."
            ),
            solution=f"You must delete a {item_type.lower()} before you can create a new one."
        )

################################################################################
