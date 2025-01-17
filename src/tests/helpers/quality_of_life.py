from __future__ import annotations

from src.dgisim.agents import *
from src.dgisim.effect.effect import *
from src.dgisim.effect.enums import DYNAMIC_CHARACTER_TARGET
from src.dgisim.effect.structs import DamageType
from src.dgisim.element.element import *
from src.dgisim.game_state_machine import GameStateMachine
from src.dgisim.helper.level_print import GamePrinter
from src.dgisim.helper.quality_of_life import *
from src.dgisim.state.enums import PID
from src.dgisim.state.game_state import GameState


def auto_step(game_state: GameState, observe: bool = False) -> GameState:
    gsm = GameStateMachine(game_state, PuppetAgent(), PuppetAgent())
    if not observe:
        gsm.auto_step()
    else:  # pragma: no cover
        while gsm.get_game_state().waiting_for() is None:
            gsm.one_step()
            print(GamePrinter.dict_game_printer(gsm.get_game_state().dict_str()))
            input(">>> ")
    return gsm.get_game_state()


def oppo_aura_elem(game_state: GameState, elem: Element, char_id: Optional[int] = None) -> GameState:
    """
    Gives Player2's active character `elem` aura
    """
    if char_id is None:
        return game_state.factory().f_player2(
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().f_active_character(
                    lambda ac: ac.factory().elemental_aura(
                        ElementalAura.from_default().add(elem)
                    ).build()
                ).build()
            ).build()
        ).build()
    else:
        return game_state.factory().f_player2(
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().f_character(
                    char_id,
                    lambda ac: ac.factory().elemental_aura(
                        ElementalAura.from_default().add(elem)
                    ).build()
                ).build()
            ).build()
        ).build()


def add_damage_effect(
        game_state: GameState,
        damage: int,
        elem: Element,
        pid: PID = PID.P2,
        char_id: Optional[int] = None,
) -> GameState:
    """
    Adds ReferredDamageEffect to Player2's active character with `damage` and `elem` from Player1's
    active character (id=1)
    """
    return game_state.factory().f_effect_stack(
        lambda es: es.push_many_fl((
            ReferredDamageEffect(
                source=StaticTarget(
                    pid.other(),
                    ZONE.CHARACTERS,
                    case_val(char_id is None, 1, char_id),  # type: ignore
                ),
                target=DYNAMIC_CHARACTER_TARGET.OPPO_ACTIVE,
                element=elem,
                damage=damage,
                damage_type=DamageType(),
            ),
            DeathCheckCheckerEffect(),
        ))
    ).build()


def kill_character(
        game_state: GameState,
        character_id: int,
        pid: PID = PID.P2,
        hp: int = 0,
) -> GameState:
    """
    Sets Player2's active character's hp to `hp` (default=0)
    """
    return game_state.factory().f_player(
        pid,
        lambda p: p.factory().f_characters(
            lambda cs: cs.factory().f_character(
                character_id,
                lambda c: c.factory().hp(hp).build()
            ).build()
        ).build()
    ).build()


def set_active_player_id(game_state: GameState, pid: PID, character_id: int) -> GameState:
    return game_state.factory().f_player(
        pid,
        lambda p: p.factory().f_characters(
            lambda cs: cs.factory().active_character_id(character_id).build()
        ).build()
    ).build()

def fill_dices_with_omni(game_state: GameState) -> GameState:
    return game_state.factory().f_player1(
        lambda p: p.factory().dices(ActualDices({Element.OMNI: BIG_INT})).build()
    ).f_player2(
        lambda p: p.factory().dices(ActualDices({Element.OMNI: BIG_INT})).build()
    ).build()
