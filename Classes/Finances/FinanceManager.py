from __future__ import annotations

from ftplib import error_perm
from typing import TYPE_CHECKING, Any, Dict, List

from discord import Interaction, User, Embed

from Classes.Common import ObjectManager
from Errors import InvalidNumber
from Utilities import Utilities as U
from .Transaction import Transaction
from UI.Common import FroggeSelectView, BasicNumberModal, ConfirmCancelView, BasicTextModal, CloseMessageView
from Enums import TransactionCategory
from UI.Finances import FinanceManagerMenuView

if TYPE_CHECKING:
    from Classes import GuildData, EventManager
    from UI.Common import FroggeView
################################################################################

__all__ = ("FinanceManager", )

################################################################################
class FinanceManager(ObjectManager):

    __slots__ = (
    )

################################################################################
    def __init__(self, state: GuildData) -> None:

        super().__init__(state)

################################################################################
    async def load_all(self, payload: Dict[str, Any]) -> None:

        self._managed = [Transaction.load(self, data) for data in payload["transactions"]]

################################################################################
    @property
    def event_manager(self) -> EventManager:

        return self._state.event_manager

################################################################################
    @property
    def transactions(self) -> List[Transaction]:

        return self._managed  # type: ignore

################################################################################
    @property
    def balance(self) -> int:

        return sum(transaction.amount for transaction in self.transactions)

################################################################################
    def update(self) -> None:

        self.bot.api.update_finance_manager(self)

################################################################################
    def to_dict(self) -> Dict[str, Any]:

        return {
            "balance": self.balance,
        }

################################################################################
    async def status(self) -> Embed:

        return U.make_embed(
            title="__Finance Overview__",
            description=(
                "**CURRENT BALANCE:**\n"
                f"**[`{self.balance:,} gil`]**\n\n"
                
                f"**[`{len(self.transactions)}`]** transactions recorded.\n"
            )
        )

################################################################################
    def get_menu_view(self, user: User) -> FroggeView:

        return FinanceManagerMenuView(user, self)

################################################################################
    async def add_item(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Select Transaction Category__",
            description=(
                "Please select the category of the transaction you're logging."
            )
        )
        view = FroggeSelectView(
            owner=interaction.user,
            options=TransactionCategory.select_options(),
            return_interaction=True
        )

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        cat_id, inter = view.value
        category = TransactionCategory(int(cat_id))

        modal = BasicTextModal(
            title="Enter Transaction Amount",
            attribute="Amount",
            example="eg. '100000' or '-500k' or '10m'",
            max_length=10
        )

        await inter.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        transaction_amount = U.parse_salary(modal.value)
        if transaction_amount is None:
            error = InvalidNumber("Transaction Amount")
            await interaction.respond(embed=error, ephemeral=True)
            return

        # Add Memo?
        prompt = U.make_embed(
            title="__Add Transaction Memo__",
            description=(
                "Would you like to enter a memo for this transaction?"
            )
        )
        view = ConfirmCancelView(
            owner=interaction.user,
            return_interaction=True,
            confirm_text="Yes",
            cancel_text="No"
        )

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete:
            return

        if view.value is False:
            memo = None
        else:
            _, inter = view.value
            modal = BasicTextModal(
                title="Enter Transaction Memo",
                attribute="Memo",
                example="eg. 'Bought a new car'",
                max_length=100,
                required=False
            )

            await inter.response.send_modal(modal)
            await modal.wait()

            if not modal.complete:
                return

            memo = modal.value

        prompt = U.make_embed(
            title="__Transaction Summary__",
            description=(
                f"**Category:** `{category.proper_name}`\n"
                f"**Amount:** `{transaction_amount:,} gil`\n"
                f"**Memo:** `{memo or 'N/A'}`\n\n"
                
                "Would you like to add tags to this transaction?"
            )
        )
        view = ConfirmCancelView(
            owner=interaction.user,
            return_interaction=True,
            confirm_text="Yes, add Tags",
            cancel_text="No, just Save"
        )

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete:
            return

        if view.value is False:
            tags = []
        else:
            _, inter = view.value
            modal = BasicTextModal(
                title="Enter Transaction Tags",
                attribute="Tags",
                example="eg. 'food, groceries, shopping'",
                max_length=200,
                required=False
            )

            await inter.response.send_modal(modal)
            await modal.wait()

            if not modal.complete:
                return

            tags = [tag.strip() for tag in modal.value.split(",")]

        await self.record_transaction(interaction, transaction_amount, category, memo, tags)

################################################################################
    async def record_transaction(
        self,
        interaction: Interaction,
        amount: int,
        category: TransactionCategory,
        memo: str,
        tags: List[str]
    ) -> None:

        new_transaction = Transaction.new(
            self,
            user_id=interaction.user.id,
            amount=amount,
            category=category,
            memo=memo,
            tags=tags
        )
        self._managed.append(new_transaction)

        confirm = U.make_embed(
            title="__Transaction Added__",
            description=(
                "The transaction has been successfully logged."
            )
        )

        await interaction.respond(embed=confirm, ephemeral=True)

################################################################################
    async def modify_item(self, interaction: Interaction) -> None:

        modal = BasicNumberModal(
            title="Enter Transaction ID",
            attribute="Transaction ID",
            example="eg. '12345'",
            max_length=10
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        transaction = self[modal.value]
        if transaction is None:
            error = U.make_error(
                title="__Transaction Not Found__",
                message="No transaction was found with the ID provided.",
                solution="Please double-check the ID and try again."
            )
            await interaction.respond(embed=error, ephemeral=True)
            return

        await transaction.menu(interaction)

################################################################################
    async def remove_item(self, interaction: Interaction) -> None:

        modal = BasicNumberModal(
            title="Enter Transaction ID",
            attribute="Transaction ID",
            example="eg. '12345'",
            max_length=10
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        transaction = self[modal.value]
        if transaction is None:
            error = U.make_error(
                title="__Transaction Not Found__",
                message="No transaction was found with the ID provided.",
                solution="Please double-check the ID and try again."
            )
            await interaction.respond(embed=error, ephemeral=True)
            return

        await transaction.remove(interaction)

################################################################################
