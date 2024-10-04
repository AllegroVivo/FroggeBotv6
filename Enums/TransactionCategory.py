from ._Enum import FroggeEnum
################################################################################
class TransactionCategory(FroggeEnum):

    Casino = 1
    Bar = 2
    VIP = 3
    Activity = 4
    Services = 5
    Salary = 6
    Bonus = 7
    Amenities = 8
    Misc = 999

################################################################################
    @property
    def proper_name(self) -> str:

        if self.value == 6:
            return "Employee Salary"
        elif self.value == 7:
            return "Employee Bonus"
        elif self.value == 999:
            return "Miscellaneous"

        return self.name
    
################################################################################
    