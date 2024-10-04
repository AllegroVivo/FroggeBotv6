from Utilities import ErrorMessage
################################################################################

__all__ = ("RoleMissing",)

################################################################################
class RoleMissing(ErrorMessage):

    def __init__(self, role_name: str):
        super().__init__(
            title="Role Missing!",
            description=f"**Missing Role:** `{role_name}`",
            message=f"The role associated with that action is missing and cannot be used.",
            solution=f"Please contact the server owner or an admin to have the role resolved.",
        )

################################################################################
        