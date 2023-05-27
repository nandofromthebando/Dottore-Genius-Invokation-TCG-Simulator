from __future__ import annotations
from typing import TypeVar
from enum import Enum

import dgisim.src.event.effect as eft
import dgisim.src.state.game_state as gs


class TriggerringEvent(Enum):
    pass


class Buffable:
    def preprocess(self):
        raise Exception("TODO")

    def react_to_event(self, game_state: gs.GameState, event: TriggerringEvent) -> gs.GameState:
        raise Exception("TODO")

    def react_to_signal(self, source: eft.StaticTarget, signal: eft.TriggeringSignal) -> tuple[eft.Effect, ...]:
        raise Exception("TODO")

    def same_type_as(self, buff: Buffable) -> bool:
        return type(self) == type(buff)

    def __str__(self) -> str:
        return self.__class__.__name__


class CharacterTalentBuff(Buffable):
    """
    Basic buff, describing character talents
    """
    pass


class EquipmentBuff(Buffable):
    """
    Basic buff, describing weapon, artifact and character unique talents
    """


class CharacterBuff(Buffable):
    """
    Basic buff, private buff to each character
    """
    pass


class TeamBuff(Buffable):
    """
    Basic buff, buff shared across the team
    """
    pass


class StuffedBuff(CharacterBuff):
    def react_to_signal(self, source: eft.StaticTarget, signal: eft.TriggeringSignal) -> tuple[eft.Effect, ...]:
        if signal is eft.TriggeringSignal.ROUND_END:
            return (eft.RemoveCharacterBuffEffect(
                source,
                type(self),
            ),)
        return ()