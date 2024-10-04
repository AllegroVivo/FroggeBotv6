from Utilities import ErrorMessage
################################################################################

__all__ = ("UserMissing",)

################################################################################
class UserMissing(ErrorMessage):

    def __init__(self, user_id: int):
        super().__init__(
            title="User Missing!",
            description=f"**Missing User:** `{user_id}`",
            message=f"The user being referenced cannot be found.",
            solution=f"Please make sure the user is still in the server.",
        )

################################################################################
        