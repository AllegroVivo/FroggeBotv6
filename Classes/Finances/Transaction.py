from __future__ import annotations

from datetime import datetime, UTC
from typing import TYPE_CHECKING, Optional, List, Type, TypeVar, Any, Dict

from discord import User, Embed, Interaction
from unicodedata import category

from Classes.Common import ManagedObject, LazyUser
from Enums import TransactionCategory
from Utilities import Utilities as U
from UI.Common import ConfirmCancelView, BasicTextModal, FroggeSelectView, InstructionsInfo
from UI.Finances import TransactionStatusView
from Errors import InvalidNumber

if TYPE_CHECKING:
    from Classes import FinanceManager, Event
    from UI.Common import FroggeView
################################################################################

__all__ = ("Transaction", )

T = TypeVar("T", bound="Transaction")

################################################################################
class Transaction(ManagedObject):

    __slots__ = (
        "_timestamp",
        "_amount",
        "_memo",
        "_user",
        "_category",
        "_tags",
        "_event_id",
        "_void",
    )

################################################################################
    def __init__(self, mgr: FinanceManager, _id: int, **kwargs) -> None:

        super().__init__(mgr, _id)

        self._user: LazyUser = LazyUser(self, kwargs.pop("user_id"))
        self._amount: int = kwargs.pop("amount")
        self._category: TransactionCategory = kwargs.pop("category")

        self._event_id: Optional[int] = kwargs.get("event_id")
        self._timestamp: datetime = kwargs.get("timestamp")
        self._memo: Optional[str] = kwargs.get("memo")
        self._tags: List[str] = kwargs.get("tags", [])
        self._void: bool = kwargs.get("void", False)

################################################################################
    @classmethod
    def new(cls: Type[T], mgr: FinanceManager, **kwargs) -> T:

        new_data = mgr.bot.api.create_transaction(mgr.guild_id, kwargs.pop("category").value, **kwargs)
        return cls(mgr, _id=new_data["id"], **new_data)

################################################################################
    @classmethod
    def load(cls: Type[T], mgr: FinanceManager, data: Dict[str, Any]) -> T:

        return cls(
            mgr=mgr,
            _id=data["id"],
            user_id=data["user_id"],
            amount=data["amount"],
            event_id=data["event_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            memo=data["memo"],
            category=TransactionCategory(data["category"]),
            tags=data["tags"],
            void=data["void"]
        )

################################################################################
    @property
    async def user(self) -> User:

        return await self._user.get()

    @user.setter
    def user(self, value: User) -> None:

        self._user.set(value)

################################################################################
    @property
    def amount(self) -> int:

        return self._amount

    @amount.setter
    def amount(self, value: int) -> None:

        self._amount = value
        self.update()

################################################################################
    @property
    def event(self) -> Optional[Event]:

        return self._mgr.event_manager[self.event_id]  # type: ignore

    @property
    def event_id(self) -> Optional[int]:

        return self._event_id

    @event_id.setter
    def event_id(self, value: Optional[int]) -> None:

        self._event_id = value
        self.update()

################################################################################
    @property
    def timestamp(self) -> datetime:

        return self._timestamp

################################################################################
    @property
    def memo(self) -> Optional[str]:

        return self._memo

    @memo.setter
    def memo(self, value: Optional[str]) -> None:

        self._memo = value
        self.update()

################################################################################
    @property
    def category(self) -> TransactionCategory:

        return self._category

    @category.setter
    def category(self, value: TransactionCategory) -> None:

        self._category = value
        self.update()

################################################################################
    @property
    def tags(self) -> List[str]:

        return self._tags

    @tags.setter
    def tags(self, value: List[str]) -> None:

        self._tags = value
        self.update()

################################################################################
    @property
    def void(self) -> bool:

        return self._void

    @void.setter
    def void(self, value: bool) -> None:

        self._void = value
        self.update()

################################################################################
    def update(self) -> None:

        self.bot.api.update_transaction(self)

################################################################################
    def to_dict(self) -> Dict[str, Any]:

        return {
            "user_id": self._user.id,
            "amount": self._amount,
            "event_id": self._event_id,
            "memo": self._memo,
            "category": self._category.value,
            "tags": self._tags,
            "void": self._void
        }

################################################################################
    def delete(self) -> None:

        self.bot.api.delete_transaction(self.id)
        self._mgr.transaction.remove(self)  # type: ignore

################################################################################
    async def status(self) -> Embed:

        return U.make_embed(
            title=f"__Transaction Status__",
            description=(
                f"**User:** {(await self.user).mention}\n"
                f"**Amount:** `{self._amount:,} gil`\n"
                f"**Category:** `{self._category.proper_name}`\n"
                f"**Timestamp:** {self._timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"**Memo:** {self._memo or '`Not Set`'}\n"
                f"**Tags:** {', '.join(self._tags) or '`None`'}\n"
                f"**Void:** `{self._void}`"
            ),
            footer_text=f"Transaction ID: {self.id}"
        )

################################################################################
    def get_menu_view(self, user: User) -> FroggeView:

        return TransactionStatusView(user, self)

################################################################################
    def process(self, balance: int) -> int:

        return balance + self._amount

################################################################################
    async def remove(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Remove Transaction__",
            description=(
                "Are you sure you want to remove this transaction?\n\n"
                
                "This action will negate any changes made by this transaction, "
                "and transaction details will not be recoverable."
            )
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        self.delete()

        confirm = U.make_embed(
            title="__Transaction Removed__",
            description=(
                "The transaction has been removed and yhe standing balance "
                "has been updated accordingly."
            )
        )
        await interaction.respond(embed=confirm, ephemeral=True)

################################################################################
    async def set_amount(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Edit Transaction Amount",
            attribute="Amount",
            cur_val=str(self.amount),
            example="eg '100000' or '-50k' or '2m'",
            max_length=12
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        amount = U.parse_salary(modal.value)
        if amount is None:
            error = InvalidNumber(modal.value)
            await interaction.respond(embed=error, ephemeral=True)
            return

        difference = amount - self.amount
        self._mgr.balance += difference  # type: ignore

        self.amount = amount

################################################################################
    async def set_category(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Set Transaction Category__",
            description=(
                "Please select the category for this transaction."
            )
        )
        view = FroggeSelectView(interaction.user, TransactionCategory.select_options())

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        self.category = TransactionCategory(int(view.value))

################################################################################
    async def set_memo(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Edit Transaction Memo",
            attribute="Memo",
            cur_val=self.memo,
            example="eg 'Giveaway prize'",
            max_length=100
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.memo = modal.value

################################################################################
    async def set_tags(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Edit Transaction Tags",
            attribute="Tags",
            cur_val=", ".join(self.tags),
            example="eg 'giveaway, prize'",
            max_length=200,
            instructions=InstructionsInfo(
                placeholder="Enter tags separated by commas",
                value="Enter a comma-separated list of tags to categorize this transaction."
            )
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.tags = [tag.strip() for tag in modal.value.split(",")]

################################################################################
    async def toggle_void(self, interaction: Interaction) -> None:

        self.void = not self.void
        await interaction.respond("** **", delete_after=0.1)

################################################################################
