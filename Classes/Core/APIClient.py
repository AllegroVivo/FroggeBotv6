from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Optional, TypeVar, Dict, Union, TYPE_CHECKING, List
from urllib.parse import quote as _uriquote

from dotenv import load_dotenv
from requests import Session

if TYPE_CHECKING:
    from Classes import *
################################################################################

__all__ = ("APIClient", )

MU = TypeVar("MU", bound="MaybeUnlock")

################################################################################
class Route:
    def __init__(self, method: str, path: str, **parameters: Any) -> None:
        
        self.path: str = path
        self.method: str = method
        
        url = self.base + self.path
        if parameters:
            url = url.format_map(
                {
                    k: _uriquote(v) if isinstance(v, str) else v
                    for k, v in parameters.items()
                }
            )
        self.url: str = url

    @property
    def base(self) -> str:
        
        load_dotenv()
        if os.getenv("DEBUG") == "True":
            return "http://127.0.0.1:8000"
        else:
            return "https://frogge-api-bdb0d124f9d8.herokuapp.com"
            
################################################################################
class APIClient:

    def __init__(self, client: FroggeBot) -> None:

        self._client: FroggeBot = client

        self.session: Session = Session()
        self.token: Optional[str] = None

################################################################################
# Primary Methods            
################################################################################
    def request(self, route: Route, _fmt: str = "json", **kwargs: Any) -> Union[Dict[str, Any], str]:

        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        if _fmt == "json":
            headers["Content-Type"] = "application/json"
            data = json.dumps(kwargs)  # Encode data as JSON
        elif _fmt == "form":
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            data = kwargs  # Send the data directly as form data (a dictionary)
        else:
            raise ValueError("Unsupported data format. Use 'json' or 'form'.")

        with self.session.request(
            route.method, route.url, data=data, headers=headers
        ) as response:
            if _fmt == "json" and response.status_code == 401:
                self.login()
                return self.request(route, _fmt=_fmt, **kwargs)
            if response.status_code >= 400:
                print(response.json())
                raise Exception(f"HTTP Error: {response.status_code}")
            return (
                response.json()
                if "application/json" in response.headers.get("Content-Type", "")
                else response.text
            )

################################################################################
    def login(self):

        load_dotenv()
        token_data = self.request(
            Route("POST", "/users/login"),
            _fmt="form",
            username=self._client.user.id,
            password=os.getenv("API_PASSWORD")
        )
        self.token = token_data["access_token"]
    
################################################################################
    def load_all(self):
        
        return self.request(Route("GET", "/load"))
    
################################################################################
    def check_guild(self, guild_id: int):

        return self.request(
            Route("GET", "/guilds"),
            guild_id=guild_id
        )

################################################################################
# Guild Level Management
################################################################################
    def update_guild_configuration(self, guild_id: int, **params: Any):
        
        return self.request(
            Route("PUT", "/guilds"),
            guild_id=guild_id,
            **params
        )
    
################################################################################
    def create_guild(self, guild_id: int):

        return self.request(
            Route("POST", "/guilds"),
            guild_id=guild_id
        )

################################################################################
# Positions Management
################################################################################
    def create_position(self, guild_id: int):
        
        return self.request(
            Route("POST", "/positions"), 
            guild_id=guild_id
        )
    
################################################################################
    def update_position(self, pos: Position):
        
        return self.request(
            Route(
                "PUT", 
                "/positions/{position_id}",
                position_id=pos.id
            ),
            **pos.to_dict()
        )
    
################################################################################
    def delete_position(self, pos: Position):
        
        return self.request(
            Route("DELETE", "/positions"),
            id=pos.id
        )

################################################################################
# VIP Management
################################################################################
    def create_vip_tier(self, guild_id: int):
        
        return self.request(
            Route("POST", "/vip/tiers"),
            guild_id=guild_id
        )
    
################################################################################
    def create_vip_member(self, guild_id: int, user_id: int, tier_id: int, end_date: Optional[datetime]):
        
        return self.request(
            Route("POST", "/vip/members"),
            guild_id=guild_id,
            user_id=user_id,
            tier_id=tier_id,
            expiry_date=end_date.isoformat() if end_date else None
        )
    
################################################################################
    def delete_vip_member(self, member_id: int):

        return self.request(
            Route("DELETE", "/vip/members"),
            id=member_id
        )

################################################################################
    def create_vip_perk(self, guild_id: int, tier_id: int):
        
        return self.request(
            Route("POST", "/vip/perks"),
            guild_id=guild_id,
            tier_id=tier_id
        )
    
################################################################################
    def create_vip_perk_override(self, member_id: int, perk_id: int, level: int):
            
        return self.request(
            Route("POST", "/vip/overrides"),
            member_id=member_id,
            perk_id=perk_id,
            level=level
        )
    
################################################################################
    def update_vip_program(self, vip: VIPManager):

        return self.request(
            Route("PUT", "/vip"),
            guild_id=vip.guild.guild_id,
            **vip.to_dict()
        )

################################################################################
    def update_vip_tier(self, tier: VIPTier):
        
        return self.request(
            Route(
                "PUT", 
                "/vip/tiers/{tier_id}",
                tier_id=tier.id
            ),
            **tier.to_dict()
        )
    
################################################################################
    def update_vip_perk(self, perk: VIPPerk):
        
        return self.request(
            Route(
                "PUT", 
                "/vip/perks/{perk_id}",
                perk_id=perk.id
            ),
            **perk.to_dict()
        )
    
################################################################################
    def update_vip_member(self, member: VIPMember):
        
        return self.request(
            Route(
                "PUT", 
                "/vip/members/{member_id}",
                member_id=member.id
            ),
            **member.to_dict()
        )
    
################################################################################
    def update_vip_perk_override(self, override: VIPPerkOverride):
        
        return self.request(
            Route(
                "PUT", 
                "/vip/overrides/{override_id}",
                override_id=override.id
            ),
            **override.to_dict()
        )
    
################################################################################
    def delete_vip_perk(self, perk: VIPPerk):
        
        return self.request(
            Route("DELETE", "/vip/perks"),
            id=perk.id
        )
    
################################################################################
    def delete_vip_perk_override(self, override: VIPPerkOverride):
        
        return self.request(
            Route("DELETE", "/vip/overrides"),
            id=override.id
        )
    
################################################################################
    def delete_vip_tier(self, tier: VIPTier):
        
        return self.request(
            Route("DELETE", "/vip/tiers"),
            id=tier.id
        )
    
################################################################################
    def update_vip_message(self, message: VIPMessage):
        
        return self.request(
            Route(
                "PUT", 
                "/vip/messages/{guild_id}",
                guild_id=message.guild_id
            ),
            **message.to_dict()
        )
    
################################################################################
# Verification Management
################################################################################
    def create_role_relation(self, guild_id: int):
        
        return self.request(
            Route("POST", "/verification/roles"),
            guild_id=guild_id
        )
    
################################################################################
    def create_user_verification(self, guild_id: int, user_id: int, char_name: str, lodestone: int):
        
        return self.request(
            Route("POST", "/verification/users"),
            guild_id=guild_id,
            user_id=user_id,
            name=char_name,
            lodestone_id=lodestone
        )
    
################################################################################
    def update_verification_config(self, config: VerificationConfig):
        
        return self.request(
            Route("PUT", "/verification"),
            guild_id=config.guild_id,
            **config.to_dict()
        )
    
################################################################################
    def update_role_relation(self, relation: VerificationRoleRelation):
        
        return self.request(
            Route(
                "PUT", 
                "/verification/roles/{relation_id}",
                relation_id=relation.id
            ),
            **relation.to_dict()
        )
    
################################################################################
    def delete_role_relation(self, relation: VerificationRoleRelation):
        
        return self.request(
            Route("DELETE", "/verification/roles"),
            id=relation.id
        )
    
################################################################################
# Profile Endpoints
################################################################################
    def create_profile(self, guild_id: int, user_id: int):

        return self.request(
            Route("POST", "/profiles"),
            guild_id=guild_id,
            user_id=user_id
        )

################################################################################
    def update_profile_requirements(self, reqs: ProfileRequirements):
        
        return self.request(
            Route(
                "PUT",
                "/profiles/requirements/{guild_id}",
                guild_id=reqs.guild_id
            ),
            **reqs.to_dict()
        )
    
################################################################################
    def create_additional_image(self, profile_id: int, url: str):
        
        return self.request(
            Route("POST", "/profiles/images"),
            profile_id=profile_id,
            image_url=url
        )
    
################################################################################
    def update_additional_image(self, image: AdditionalImage):
        
        return self.request(
            Route(
                "PUT", 
                "/profiles/aimages/{image_id}",
                image_id=image.id
            ),
            **image.to_dict()
        )
    
################################################################################
    def delete_additional_image(self, image: AdditionalImage):
        
        return self.request(
            Route("DELETE", "/profiles/images"),
            id=image.id
        )

################################################################################
    def create_profile_channel_group(self, guild_id: int):
        
        return self.request(
            Route("POST", "/profiles/channels"),
            guild_id=guild_id
        )

################################################################################
    def update_profile_channel_group(self, group: ProfileChannelGroup):
        
        return self.request(
            Route(
                "PUT", 
                "/profiles/channels/{group_id}",
                group_id=group.id
            ),
            **group.to_dict()
        )
    
################################################################################
    def delete_profile_channel_group(self, group: ProfileChannelGroup):
        
        return self.request(
            Route("DELETE", "/profiles/channels"),
            id=group.id
        )
    
################################################################################
    def update_profile(self, profile: Profile):
        
        return self.request(
            Route(
                "PUT", 
                "/profiles/{profile_id}",
                profile_id=profile.id
            ),
            **profile.to_dict()
        )
    
################################################################################
    def update_profile_ataglance(self, ataglance: ProfileAtAGlance):

        return self.request(
            Route(
                "PUT",
                "/profiles/ataglance/{profile_id}",
                profile_id=ataglance.parent.id
            ),
            **ataglance.to_dict()
        )

################################################################################
    def update_profile_details(self, details: ProfileDetails):

        return self.request(
            Route(
                "PUT",
                "/profiles/details/{profile_id}",
                profile_id=details.parent.id
            ),
            **details.to_dict()
        )

################################################################################
    def update_profile_images(self, images: ProfileImages):

        return self.request(
            Route(
                "PUT",
                "/profiles/images/{profile_id}",
                profile_id=images.parent.id
            ),
            **images.to_dict()
        )

################################################################################
    def update_profile_personality(self, personality: ProfilePersonality):

        return self.request(
            Route(
                "PUT",
                "/profiles/personality/{profile_id}",
                profile_id=personality.parent.id
            ),
            **personality.to_dict()
        )

################################################################################
# Staffing Endpoints
################################################################################
    def create_staff_character(self, staff_id: int, name: str, profile_id: int):

        return self.request(
            Route("POST", "/staffing/characters"),
            staff_id=staff_id,
            name=name,
            profile_id=profile_id
        )

################################################################################
    def update_staff_character(self, character: StaffCharacter):

        return self.request(
            Route(
                "PUT",
                "/staffing/characters/{character_id}",
                character_id=character.id
            ),
            **character.to_dict()
        )

################################################################################
    def delete_staff_character(self, character_id: int):

        return self.request(
            Route("DELETE", "/staffing/characters"),
            id=character_id
        )

################################################################################
    def create_employment_date(self, staff_id: int):

        return self.request(
            Route("POST", "/staffing/dates"),
            staff_id=staff_id
        )

################################################################################
    def update_employment_date(self, date: EmploymentPeriod):

        return self.request(
            Route(
                "PUT",
                "/staffing/dates/{date_id}",
                date_id=date.id
            ),
            **date.to_dict()
        )

################################################################################
    def delete_employment_date(self, date_id: int):

        return self.request(
            Route("DELETE", "/staffing/dates"),
            id=date_id
        )

################################################################################
    def update_staff_manager(self, mgr: StaffManager):

        return self.request(
            Route(
                "PUT",
                "/staffing/{guild_id}",
                guild_id=mgr.guild_id,
            ),
            **mgr.to_dict()
        )

################################################################################
    def create_staff_member(self, guild_id: int, user_id: int, name: str):

        return self.request(
            Route("POST", "/staffing/staff"),
            guild_id=guild_id,
            user_id=user_id,
            name=name
        )

################################################################################
    def delete_staff_member(self, staff_id: int):

        return self.request(
            Route("DELETE", "/staffing/staff"),
            staff_id=staff_id
        )

################################################################################
    def update_staff_member(self, staff: StaffMember):

        return self.request(
            Route(
                "PUT",
                "/staffing/staff/{staff_id}",
                staff_id=staff.id
            ),
            **staff.to_dict()
        )

################################################################################
    def update_staff_details(self, details: StaffDetails):

        return self.request(
            Route(
                "PUT",
                "/staffing/details/{staff_id}",
                staff_id=details._parent.id
            ),
            **details.to_dict()
        )

################################################################################
# Forms Endpoints
################################################################################
    def create_form(self, guild_id: int, name: str):

        return self.request(
            Route("POST", "/forms"),
            guild_id=guild_id,
            form_name=name
        )

################################################################################
    def delete_form(self, form_id: int):

        return self.request(
            Route("DELETE", "/forms"),
            id=form_id
        )

################################################################################
    def update_form(self, form: Form):

        return self.request(
            Route(
                "PUT",
                "/forms/{form_id}",
                form_id=form.id
            ),
            **form.to_dict()
        )

################################################################################
    def create_form_question(self, form_id: int):

        return self.request(
            Route("POST", "/forms/questions"),
            id=form_id
        )

################################################################################
    def update_form_question(self, question: FormQuestion):

        return self.request(
            Route(
                "PUT",
                "/forms/questions/{question_id}",
                question_id=question.id
            ),
            **question.to_dict()
        )

################################################################################
    def delete_form_question(self, question_id: int):

        return self.request(
            Route("DELETE", "/forms/questions"),
            id=question_id
        )

################################################################################
    def create_form_response_collection(self, form_id: int, user_id, q: List[str], r: List[str]):

        return self.request(
            Route("POST", "/forms/collections"),
            form_id=form_id,
            user_id=user_id,
            questions=q,
            responses=r
        )

################################################################################
    def create_form_option(self, question_id: int):

        return self.request(
            Route("POST", "/forms/options"),
            id=question_id
        )

################################################################################
    def update_form_option(self, option: FormOption):

        return self.request(
            Route(
                "PUT",
                "/forms/options/{option_id}",
                option_id=option.id
            ),
            **option.to_dict()
        )

################################################################################
    def create_form_question_prompt(self, question_id: int, prompt_type: int):

        return self.request(
            Route("POST", "/forms/questions/prompts"),
            question_id=question_id,
            prompt_type=prompt_type
        )

################################################################################
    def update_form_question_prompt(self, prompt: FormQuestionPrompt):

        return self.request(
            Route(
                "PUT",
                "/forms/questions/prompts/{prompt_id}",
                prompt_id=prompt.id
            ),
            **prompt.to_dict()
        )

################################################################################
    def update_form_post_options(self, options: FormPostOptions):

        return self.request(
            Route(
                "PUT",
                "/forms/post_options/{form_id}",
                form_id=options._parent.id
            ),
            **options.to_dict()
        )

################################################################################
    def delete_form_option(self, option_id: int):

        return self.request(
            Route("DELETE", "/forms/options"),
            id=option_id
        )

################################################################################
    def create_form_response(self, question_id: int, user_id: int, response: List[str]):

        return self.request(
            Route("POST", "/forms/responses"),
            question_id=question_id,
            user_id=user_id,
            values=response
        )

################################################################################
    def delete_form_response(self, question_id: int, user_id: int):

        return self.request(
            Route("DELETE", "/forms/responses"),
            question_id=question_id,
            user_id=user_id
        )

################################################################################
    def create_form_prompt(self, form_id: int, prompt_type: int):

        return self.request(
            Route("POST", "/forms/prompts"),
            id=form_id,
            prompt_type=prompt_type
        )

################################################################################
    def update_form_prompt(self, prompt: FormPrompt):

        return self.request(
            Route(
                "PUT",
                "/forms/prompts/{prompt_id}",
                prompt_id=prompt.id
            ),
            **prompt.to_dict()
        )

################################################################################
# Events Endpoints
################################################################################
    def update_event_system(self, event_system: EventManager):

        return self.request(
            Route(
                "PUT",
                "/events/manager/{guild_id}",
                guild_id=event_system.guild.guild_id
            ),
            **event_system.to_dict()
        )

################################################################################
    def update_event(self, event: Event):

        return self.request(
            Route(
                "PUT",
                "/events/{event_id}",
                event_id=event.id
            ),
            **event.to_dict()
        )

################################################################################
    def create_event_element(self, event_id: int, element_type: int):

        return self.request(
            Route("POST", "/events/elements"),
            event_id=event_id,
            element_type=element_type
        )

################################################################################
    def update_event_element(self, element: EventElement):

        return self.request(
            Route(
                "PUT",
                "/events/elements/{element_id}",
                element_id=element.id
            ),
            **element.to_dict()
        )

################################################################################
    def delete_event_element(self, element_id: int):

        return self.request(
            Route("DELETE", "/events/elements"),
            id=element_id
        )

################################################################################
    def create_shift_bracket(self, event_id: int, start_time: datetime, end_time: datetime):

        return self.request(
            Route("POST", "/events/shifts"),
            event_id=event_id,
            start_time=start_time.isoformat() if start_time else None,
            end_time=end_time.isoformat() if end_time else None
        )

################################################################################
    def create_event_position(self, event_id: int, pos_id: int, qty: int):

        return self.request(
            Route("POST", "/events/positions"),
            event_id=event_id,
            position_id=pos_id,
            quantity=qty
        )

################################################################################
    def update_shift_bracket(self, bracket: ShiftBracket):

        return self.request(
            Route(
                "PUT",
                "/events/shifts/{bracket_id}",
                bracket_id=bracket.id
            ),
            **bracket.to_dict()
        )

################################################################################
    def delete_shift_bracket(self, bracket_id: int):

        return self.request(
            Route("DELETE", "/events/shifts"),
            id=bracket_id
        )

################################################################################
    def update_event_position(self, position: EventPosition):

        return self.request(
            Route(
                "PUT",
                "/events/positions/{position_id}",
                position_id=position.id
            ),
            **position.to_dict()
        )

################################################################################
    def delete_event_position(self, position_id: int):

        return self.request(
            Route("DELETE", "/events/positions"),
            id=position_id
        )

################################################################################
    def create_event(self, guild_id: int):

        return self.request(
            Route("POST", "/events"),
            guild_id=guild_id
        )

################################################################################
    def delete_event(self, event_id: int):

        return self.request(
            Route("DELETE", "/events"),
            id=event_id
        )

################################################################################
    def create_event_signup(self, position_id: int, staff_id: int, bracket_id: int):

        return self.request(
            Route("POST", "/events/signups"),
            position_id=position_id,
            staff_id=staff_id,
            bracket_id=bracket_id
        )

################################################################################
    def delete_event_signup(self, signup_id: int):

        return self.request(
            Route("DELETE", "/events/signups"),
            id=signup_id
        )

################################################################################
# Giveaway Endpoints
################################################################################
    def create_giveaway(self, guild_id: int):

        return self.request(
            Route("POST", "/giveaways"),
            guild_id=guild_id
        )

################################################################################
    def update_giveaway_details(self, details: GiveawayDetails):

        return self.request(
            Route(
                "PUT",
                "/giveaways/details/{giveaway_id}",
                giveaway_id=details.parent_id
            ),
            **details.to_dict()
        )

################################################################################
    def create_giveaway_entry(self, giveaway_id: int, user_id: int):

        return self.request(
            Route("POST", "/giveaways/entries"),
            giveaway_id=giveaway_id,
            user_id=user_id
        )

################################################################################
    def delete_giveaway_entry(self, entry_id: int):

        return self.request(
            Route("DELETE", "/giveaways/entries"),
            id=entry_id
        )

################################################################################
    def update_giveaway(self, giveaway: Giveaway):

        return self.request(
            Route(
                "PUT",
                "/giveaways/{giveaway_id}",
                giveaway_id=giveaway.id
            ),
            **giveaway.to_dict()
        )

################################################################################
    def delete_giveaway(self, giveaway_id: int):

        return self.request(
            Route("DELETE", "/giveaways"),
            id=giveaway_id
        )

################################################################################
# Raffle Endpoints
################################################################################
    def create_raffle(self, guild_id: int, is_active: bool):

        return self.request(
            Route("POST", "/raffles"),
            guild_id=guild_id,
            is_active=is_active
        )

################################################################################
    def update_raffle_manager(self, mgr: RaffleManager):

        return self.request(
            Route(
                "PUT",
                "/raffles/manager/{guild_id}",
                guild_id=mgr.guild_id
            ),
            **mgr.to_dict()
        )

################################################################################
    def update_raffle(self, raffle: Raffle):

        return self.request(
            Route(
                "PUT",
                "/raffles/{raffle_id}",
                raffle_id=raffle.id
            ),
            **raffle.to_dict()
        )

################################################################################
    def delete_raffle(self, raffle_id: int):

        return self.request(
            Route("DELETE", "/raffles"),
            id=raffle_id
        )

################################################################################
    def create_raffle_entry(self, raffle_id: int, user_id: int, qty: int):

        return self.request(
            Route("POST", "/raffles/entries"),
            raffle_id=raffle_id,
            user_id=user_id,
            quantity=qty
        )

################################################################################
    def delete_raffle_entry(self, entry_id: int):

        return self.request(
            Route("DELETE", "/raffles/entries"),
            id=entry_id
        )

################################################################################
    def update_raffle_entry(self, entry: RaffleEntry):

        return self.request(
            Route(
                "PUT",
                "/raffles/entries/{entry_id}",
                entry_id=entry.id
            ),
            **entry.to_dict()
        )

################################################################################
    def update_raffle_details(self, details: RaffleDetails):

        return self.request(
            Route(
                "PUT",
                "/raffles/details/{raffle_id}",
                raffle_id=details.parent_id
            ),
            **details.to_dict()
        )

################################################################################
# Reaction Role Endpoints
################################################################################
    def create_reaction_role_message(self, guild_id: int):

        return self.request(
            Route("POST", "/roles/messages"),
            guild_id=guild_id
        )

################################################################################
    def create_reaction_role(self, message_id: int):

        return self.request(
            Route("POST", "/roles/roles"),
            id=message_id
        )

################################################################################
    def delete_reaction_role_message(self, message_id: int):

        return self.request(
            Route("DELETE", "/roles/messages"),
            id=message_id
        )

################################################################################
    def delete_reaction_role(self, role_id: int):

        return self.request(
            Route("DELETE", "/roles/roles"),
            id=role_id
        )

################################################################################
    def update_reaction_role_message(self, message: ReactionRoleMessage):

        return self.request(
            Route(
                "PUT",
                "/roles/messages/{message_id}",
                message_id=message.id
            ),
            **message.to_dict()
        )

################################################################################
    def update_reaction_role(self, role: ReactionRole):

        return self.request(
            Route(
                "PUT",
                "/roles/roles/{role_id}",
                role_id=role.id
            ),
            **role.to_dict()
        )

################################################################################
    def update_reaction_role_manager(self, mgr: ReactionRoleManager):

        return self.request(
            Route(
                "PUT",
                "/roles/{guild_id}",
                guild_id=mgr.guild_id
            ),
            **mgr.to_dict()
        )

################################################################################
# Room Endpoints
################################################################################
    def create_room(self, guild_id: int, index: int):

        return self.request(
            Route("POST", "/rooms"),
            guild_id=guild_id,
            index=index
        )

################################################################################
    def delete_room(self, room_id: int):

        return self.request(
            Route("DELETE", "/rooms"),
            id=room_id
        )

################################################################################
    def update_room(self, room: Room):

        return self.request(
            Route(
                "PUT",
                "/rooms/room/{room_id}",
                room_id=room.id
            ),
            **room.to_dict()
        )

################################################################################
    def update_room_manager(self, mgr: RoomsManager):

        return self.request(
            Route(
                "PUT",
                "/rooms/{guild_id}",
                guild_id=mgr.guild_id
            ),
            **mgr.to_dict()
        )

################################################################################
    def update_room_details(self, details: RoomDetails):

        return self.request(
            Route(
                "PUT",
                "/rooms/details/{room_id}",
                room_id=details._parent.id
            ),
            **details.to_dict()
        )

################################################################################
    def create_room_image(self, room_id: int, url: str):

        return self.request(
            Route("POST", "/rooms/images"),
            room_id=room_id,
            url=url
        )

################################################################################
    def delete_room_image(self, image_id: int):

        return self.request(
            Route("DELETE", "/rooms/images"),
            id=image_id
        )

################################################################################
# Embed Endpoints
################################################################################
    def create_embed(self, guild_id: int):

        return self.request(
            Route("POST", "/embeds"),
            guild_id=guild_id
        )

################################################################################
    def delete_embed(self, embed_id: int):

        return self.request(
            Route("DELETE", "/embeds"),
            id=embed_id
        )

################################################################################
    def update_embed(self, embed: FroggeEmbed):

        return self.request(
            Route(
                "PUT",
                "/embeds/{embed_id}",
                embed_id=embed.id
            ),
            **embed.to_dict()
        )

################################################################################
    def create_embed_field(self, embed_id: int):

        return self.request(
            Route("POST", "/embeds/fields"),
            id=embed_id
        )

################################################################################
    def update_embed_field(self, field: FroggeEmbedField):

        return self.request(
            Route(
                "PUT",
                "/embeds/fields/{field_id}",
                field_id=field.id
            ),
            **field.to_dict()
        )

################################################################################
    def delete_embed_field(self, field_id: int):

        return self.request(
            Route("DELETE", "/embeds/fields"),
            id=field_id
        )

################################################################################
    def update_embed_header(self, header: FroggeEmbedHeader):

        return self.request(
            Route(
                "PUT",
                "/embeds/headers/{embed_id}",
                embed_id=header.parent_id
            ),
            **header.to_dict()
        )

################################################################################
    def update_embed_footer(self, footer: FroggeEmbedFooter):

        return self.request(
            Route(
                "PUT",
                "/embeds/footers/{embed_id}",
                embed_id=footer.parent_id
            ),
            **footer.to_dict()
        )

################################################################################
    def update_embed_images(self, images: FroggeEmbedImages):

        return self.request(
            Route(
                "PUT",
                "/embeds/images/{embed_id}",
                embed_id=images.parent_id
            ),
            **images.to_dict()
        )

################################################################################
# Finance Endpoints
################################################################################
    def create_transaction(self, guild_id: int, category: int, **data: Dict[str, Any]):

        return self.request(
            Route("POST", "/finance/transaction"),
            guild_id=guild_id,
            category=category,
            **data
        )

################################################################################
    def delete_transaction(self, transaction_id: int):

        return self.request(
            Route("DELETE", "/finance/transaction"),
            id=transaction_id
        )

################################################################################
    def update_transaction(self, transaction: Transaction):

        return self.request(
            Route(
                "PUT",
                "/finance/transaction/{transaction_id}",
                transaction_id=transaction.id
            ),
            **transaction.to_dict()
        )

################################################################################
    def update_finance_manager(self, mgr: FinanceManager):

        return self.request(
            Route(
                "PUT",
                "/finance/{guild_id}",
                guild_id=mgr.guild_id
            ),
            **mgr.to_dict()
        )

################################################################################
# Messages Endpoints
################################################################################
    def create_pf_message(self, guild_id: int, name: str):

        return self.request(
            Route("POST", "/messages"),
            guild_id=guild_id,
            name=name
        )

################################################################################
    def update_pf_message(self, message: PFMessage):

        return self.request(
            Route(
                "PUT",
                "/messages/{message_id}",
                message_id=message.id
            ),
            **message.to_dict()
        )

################################################################################
    def delete_pf_message(self, message_id: int):

        return self.request(
            Route("DELETE", "/messages"),
            id=message_id
        )

################################################################################
