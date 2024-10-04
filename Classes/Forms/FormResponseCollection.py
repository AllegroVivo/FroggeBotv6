from __future__ import annotations

from typing import TYPE_CHECKING, List, Type, TypeVar, Any, Dict

from discord import User, Embed, EmbedField

from Classes.Common import Identifiable, LazyUser
from Utilities import Utilities as U

if TYPE_CHECKING:
    from Classes import Form, GuildData
################################################################################

__all__ = ("FormResponseCollection", )

FRC = TypeVar("FRC", bound="FormResponseCollection")

################################################################################
class FormResponseCollection(Identifiable):

    __slots__ = (
        "_parent",
        "_user",
        "_questions",
        "_responses"
    )
    
################################################################################
    def __init__(self, parent: Form, _id: int, **kwargs) -> None:

        super().__init__(_id)

        self._parent: Form = parent
        self._user: LazyUser = LazyUser(self, kwargs.get("user_id"))
        
        self._questions: List[str] = kwargs.get("questions", [])
        self._responses: List[str] = kwargs.get("responses", [])
    
################################################################################
    @classmethod
    def new(cls: Type[FRC], parent: Form, user: User, q: List[str], r: List[str]) -> FRC:
        
        new_id = parent.bot.api.create_form_response_collection(parent.id, user.id, q, r)
        return cls(parent, new_id, user_id=user.id, questions=q, responses=r)
    
################################################################################
    @classmethod
    def load(cls: Type[FRC], parent: Form, data: Dict[str, Any]) -> FRC:
        
        self: FRC = cls.__new__(cls)

        self._id = data["id"]
        self._parent = parent
        self._user = LazyUser(self, data["user_id"])

        self._questions = data["questions"]
        self._responses = data["responses"]

        return self
    
################################################################################
    @property
    def guild(self) -> GuildData:

        return self._parent.guild

################################################################################
    @property
    async def user(self) -> User:
        
        return await self._user.get()
    
################################################################################
    @property
    def questions(self) -> List[str]:
        
        return self._questions
    
################################################################################
    @property
    def responses(self) -> List[str]:
        
        return self._responses
    
################################################################################
    async def compile(self) -> Embed:

        fields = []
        for question, response in zip(self.questions, self.responses):
            fields.append(EmbedField(name=question, value=response, inline=False))

        user = await self.user
        return U.make_embed(
            title=f"Application Responses for {user.display_name}",
            description=f"({user.mention})",
            fields=fields
        )

################################################################################
