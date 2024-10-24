from typing import Optional
################################################################################

__all__ = ("InstructionsInfo",)

################################################################################
class InstructionsInfo:
    
    __slots__ = (
        "_title",
        "_placeholder",
        "_value",
    )

################################################################################
    def __init__(self, placeholder: str, value: str, title: Optional[str] = None) -> None:

        self._title: Optional[str] = title
        self._placeholder: str = placeholder
        self._value: str = value
        
################################################################################
    @property
    def title(self) -> str:

        return self._title

################################################################################
    @property
    def placeholder(self) -> str:
        
        return self._placeholder
    
################################################################################
    @property
    def value(self) -> str:
        
        return self._value
    
################################################################################
