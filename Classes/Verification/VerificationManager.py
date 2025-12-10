from __future__ import annotations

import os
import random
import uuid
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from captcha.image import ImageCaptcha
from discord import (
    Interaction,
    User,
    Embed,
    EmbedField,
    TextChannel,
    File,
    NotFound,
    Forbidden,
    SelectOption
)

from Assets import BotEmojis
from Classes.Common import ObjectManager
from Enums import GameWorld
from Errors import MaxItemsReached, InsufficientPermissions, UnableToVerify
from UI.Common import FroggeSelectView, ConfirmCancelView
from UI.Verification import VerificationManagerMenuView, CharacterNameModal, HomeWorldSelectView
from Utilities import Utilities as U
from .VerificationConfig import VerificationConfig
from .VerificationData import VerificationData
from .VerificationRoleRelation import VerificationRoleRelation

if TYPE_CHECKING:
    from Classes import GuildData
    from UI.Common import FroggeView
################################################################################

__all__ = ("VerificationManager", )

################################################################################
class VerificationManager(ObjectManager):

    __slots__ = (
        "_config",
        "_void",
        "_relations",
    )

    CAPTCHA_VOID = 1260812137220149268
    
################################################################################
    def __init__(self, state: GuildData) -> None:

        super().__init__(state)
        
        self._config: VerificationConfig = VerificationConfig(self)
        self._void: TextChannel = None  # type: ignore
        self._relations: List[VerificationRoleRelation] = []
    
################################################################################
    async def load_all(self, payload: Dict[str, Any]) -> None:

        self._managed = [
            VerificationData.load(self, verification)
            for verification
            in payload["verifications"]
        ]

        self._config.load(payload["config"])
        self._void = await self.bot.fetch_channel(self.CAPTCHA_VOID)
        
        self._relations = [
            await VerificationRoleRelation.load(self, relation)
            for relation
            in payload["role_relations"]
        ]

################################################################################
    async def status(self) -> Embed:

        col1 = col2 = col3 = ""
        for relation in self._relations:
            pending_role = await relation.pending_role
            final_role = await relation.final_role
            col1 += (
                f"{pending_role.mention}\n"
                if pending_role is not None
                else "`Pending Role Not Set`\n"
            )
            col2 += f"{BotEmojis.ArrowRight}{BotEmojis.ArrowRight}{BotEmojis.ArrowRight}\n"
            col3 += (
                f"{final_role.mention}\n"
                if final_role is not None
                else "`Final Role Not Set`\n"
            )

        if not col1:
            col1 = "`No Relations`"
            col2 = col3 = "** **"

        def check(value: bool) -> str:
            return str(BotEmojis.Check) if value else str(BotEmojis.Cross)

        verified_role = await self._config.role
        return U.make_embed(
            title="__Verification Module Status__",
            description=(
                "**[Log Events]**: *Whether or not to log verification events "
                "to the server log stream.*\n"
                "**[Verified Role]**: *The role that will always be added "
                "to users upon successful verification.*\n"
                "**[Change Name]**: *Users' server display names will be "
                "force-changed to their character name upon successful "
                "verification*\n"
                "**[Require Captcha]**: *Users must complete a captcha "
                "to verify their human-ness.*\n"
                "**[Require 2FA]**: *Users must verify ownership of their "
                "character by entering a code on their Lodestone profile.*\n"
                "**[Role Relations]**: *The roles that will be swapped "
                "upon successful verification.*"
            ),
            fields=[
                EmbedField(
                    name="Log Events",
                    value=check(self._config.log_events),
                    inline=True
                ),
                EmbedField(
                    name="Verified Role",
                    value=verified_role.mention if verified_role is not None else "`Not Set`",
                    inline=True
                ),
                EmbedField(
                    name="Change Name",
                    value=check(self._config.change_name),
                    inline=True
                ),
                EmbedField(
                    name="Require Captcha",
                    value=check(self._config.require_captcha),
                    inline=True
                ),
                EmbedField(
                    name="Require 2FA",
                    value=check(self._config.require_2fa),
                    inline=True
                ),
                EmbedField("** **", "** **", True),
                EmbedField(
                    name="__Role Relations__",
                    value=col1,
                    inline=True
                ),
                EmbedField(
                    name="** **",
                    value=col2,
                    inline=True
                ),
                EmbedField(
                    name="** **",
                    value=col3,
                    inline=True
                )
            ]
        )

################################################################################
    def get_menu_view(self, user: User) -> FroggeView:

        return VerificationManagerMenuView(user, self)

################################################################################
    async def add_item(self, interaction: Interaction) -> None:

        if len(self._relations) >= self.MAX_ITEMS:
            error = MaxItemsReached("Role Relationships", self.MAX_ITEMS)
            await interaction.respond(embed=error)
            return

        new_relation = VerificationRoleRelation.new(self)
        self._relations.append(new_relation)

        await new_relation.menu(interaction)

################################################################################
    async def modify_item(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Modify Role Relation__",
            description=(
                "Please select the role relation you would like to modify."
            )
        )
        view = FroggeSelectView(
            owner=interaction.user,
            options=[await r.select_option() for r in self._relations]
        )

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        relation = self.get_relation(int(view.value))
        await relation.menu(interaction)

################################################################################
    def get_relation(self, relation_id: int) -> VerificationRoleRelation:

        return next((r for r in self._relations if r.id == relation_id), None)
    
################################################################################
    async def remove_item(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Remove Role Relation__",
            description=(
                "Please select the role relation you would like to remove."
            )
        )
        view = FroggeSelectView(
            owner=interaction.user,
            options=[await r.select_option() for r in self._relations]
        )

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        relation = self.get_relation(int(view.value))
        await relation.remove(interaction)

################################################################################
    async def toggle_logging(self, interaction: Interaction) -> None:

        await self._config.toggle_logging(interaction)

################################################################################
    async def toggle_captcha(self, interaction: Interaction) -> None:

        await self._config.toggle_captcha(interaction)

################################################################################
    async def toggle_change_name(self, interaction: Interaction) -> None:

        await self._config.toggle_change_name(interaction)

################################################################################
    async def toggle_2fa(self, interaction: Interaction) -> None:

        await self._config.toggle_2fa(interaction)

################################################################################
    async def verify(self, interaction: Interaction) -> None:

        # Step 1: Please verify you are human (Captcha)
        inter = None
        if self._config.require_captcha:
            inter = await self.verify_captcha(interaction)
            if inter is None:
                return

        interaction = inter or interaction
        forename = surname = None

        if self._config.require_2fa or self._config.change_name:
            # Step 2: Enter Name and World
            raw = await self.get_name_and_world(interaction)
            if raw is None:
                return

            forename, surname, _ = raw

            character_id = await self.bot.lodestone.fetch_character_id(interaction, *raw)
            if character_id is None:
                return

            # Step 3: 2FA Verification
            if self._config.require_2fa:
                if await self.secondary_verification(interaction, character_id):
                    verification = VerificationData.new(
                        mgr=self,
                        user=interaction.user,
                        name=f"{forename} {surname}",
                        lodestone_id=character_id
                    )
                    self._managed.append(verification)

            # Step 4: Change server nickname
            if self._config.change_name:
                await self.set_server_nickname(interaction, character_id)

        # Step 5: Swap Roles
        message_str = ""
        member = await self.guild.get_or_fetch_member(interaction.user.id)

        if self._config._role.id is not None:
            role = await self._config.role
            try:
                await member.add_roles(role)
                message_str += f"Added {role.mention} role\n"
            except Forbidden:
                error = InsufficientPermissions(None, "Add Roles")
                await interaction.respond(embed=error, ephemeral=True)
                return

        for roles in self._relations:
            result = await roles.check_swap(interaction, member)
            if result is not None:
                message_str += (result + "\n")

        # Step 6: Log Verification
        if self._config.log_events:
            if forename is not None:
                await self.guild.log.verification_submitted(interaction.user, f"{forename} {surname}")
            else:
                await self.guild.log.verification_submitted(interaction.user, "Character Verification Off")

        await interaction.respond(message_str or f"Success! You are now verified.", ephemeral=True)

################################################################################
    async def verify_captcha(self, interaction: Interaction) -> Optional[Interaction]:

        try:
            await interaction.response.defer(invisible=False)
        except:
            pass

        code = str(random.randint(100000, 999999))
        fp = f"Files/{code}captcha.png"

        captcha = ImageCaptcha()
        captcha.write(code, fp)

        file = File(fp, filename="captcha.png")
        if self._void is None:
            self._void = await self.bot.fetch_channel(self.CAPTCHA_VOID)
        message = await self._void.send(file=file)
        image_url = message.attachments[0].url

        options = [SelectOption(label=code, value=code)]
        for i in range(1, 5):
            dummy_code = str(random.randint(100000, 999999))
            options.append(
                SelectOption(
                    label=dummy_code,
                    value=dummy_code
                )
            )
        random.shuffle(options)

        prompt = U.make_embed(
            title="__Human Verification__",
            description=(
                "Please verify you are human by selecting the following "
                "code from the drop-down.\n\n"

                f"If you are unable to see the image, [please click here]({image_url})."
            ),
            image_url=image_url
        )
        view = FroggeSelectView(interaction.user, options, return_interaction=True)

        inter = await interaction.respond(embed=prompt, view=view, ephemeral=True)
        await view.wait()

        if not view.complete or view.value is False:
            return

        resp, inter2 = view.value

        if resp != code:
            error = UnableToVerify()
            await interaction.respond(embed=error, ephemeral=True)
            return

        try:
            await inter.delete()
        except NotFound:
            pass

        try:
            os.remove(fp)
        except:
            pass

        return inter2

################################################################################
    async def get_name_and_world(self, interaction: Interaction) -> Optional[Tuple[str, str, GameWorld]]:

        modal = CharacterNameModal()

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        forename, surname = modal.value

        prompt = U.make_embed(
            title="__World Selection__",
            description="Please select the data center and world your character is on."
        )
        view = HomeWorldSelectView(interaction.user)

        await interaction.respond(embed=prompt, view=view, ephemeral=True)
        await view.wait()

        if not view.complete or view.value is False:
            return

        _, world = view.value

        character_id = await self.bot.lodestone.fetch_character_id(interaction, forename, surname, world)
        if character_id is None:
            return

        return forename, surname, world

################################################################################
    async def secondary_verification(self, interaction: Interaction, character_id: int) -> bool:

        prompt = U.make_embed(
            title="__Secure Character Verification__",
            description=(
                "Would you like to perform 2-Step Verification on your character?\n\n"

                "This will require you to log into the Lodestone and enter a code "
                "in your character's bio to verify your ownership of the character."
            )
        )
        view = ConfirmCancelView(interaction.user, confirm_text="Yes", cancel_text="No")

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete:
            return False
        elif view.value is False:
            return True

        verified = await self.verify_character_two_step(interaction, character_id)
        if not verified:
            return False

        return True

################################################################################
    async def verify_character_two_step(self, interaction: Interaction, char_id: int) -> bool:

        verification_code = uuid.uuid4().hex
        prompt = U.make_embed(
            title="__2-Step Verification__",
            description=(
                "Please [log into the Lodestone](https://na.finalfantasyxiv.com/lodestone/account/login/) "
                "and enter the following code into your character's bio:\n"

                f"```{verification_code}```\n"

                "Once you have done this, please click the 'Confirm' button below to verify."
            )
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            error = UnableToVerify()
            await interaction.respond(embed=error, ephemeral=True)
            return False

        bio = await self.bot.lodestone.fetch_character_bio(interaction, char_id)

        if verification_code not in bio:
            error = U.make_error(
                title="Invalid Profile Verification Code",
                message="The verification code provided could not be found in your character's bio section.",
                solution=(
                    "Your character could not be verified. You will need to run the "
                    "command once more to try again."
                )
            )
            await interaction.respond(embed=error, ephemeral=True)
            return False

        return True

################################################################################
    async def set_server_nickname(self, interaction: Interaction, character_id: int) -> bool:

        char_name = await self.bot.lodestone.fetch_character_name(interaction, character_id)
        member = await self._state.get_or_fetch_member(interaction.user.id)

        if char_name is None or member is None:
            error = UnableToVerify()
            await interaction.respond(embed=error, ephemeral=True)
            return False

        try:
            await member.edit(nick=char_name)
        except Forbidden:
            error = InsufficientPermissions(None, "Change Nicknames")
            await interaction.respond(embed=error, ephemeral=True)
            return False
        except:
            error = UnableToVerify()
            await interaction.respond(embed=error, ephemeral=True)
            return False
        else:
            return True

################################################################################
    async def set_verified_role(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Set Verified Role__",
            description=(
                "Please mention the role that you would like to be added to users "
                "upon successful verification."
            )
        )

        role = await U.listen_for(interaction, prompt, U.MentionableType.Role)
        if role is None:
            return

        self._config.role = role

################################################################################
    async def remove_verified_role(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Remove Verified Role__",
            description=(
                "Are you sure you want to remove the verified role?"
            )
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        self._config.role = None

################################################################################
