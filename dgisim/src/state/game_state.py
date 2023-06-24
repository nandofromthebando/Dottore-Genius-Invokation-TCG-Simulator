from __future__ import annotations
from typing import Optional, Union, cast, Callable
from enum import Enum

import dgisim.src.mode as md
import dgisim.src.phase.phase as ph
import dgisim.src.phase.game_end_phase as gep
import dgisim.src.state.player_state as pl
import dgisim.src.status.status as stt
import dgisim.src.action as act
from dgisim.src.helper.level_print import level_print, level_print_single, INDENT
from dgisim.src.helper.quality_of_life import case_val
from dgisim.src.action import PlayerAction
from dgisim.src.effect.effect_stack import EffectStack
from dgisim.src.event.event_pre import EventPre
from dgisim.src.character.character import Character
from dgisim.src.effect.effect import StaticTarget, Zone
from dgisim.src.event.event import *


class GameState:
    class Pid(Enum):
        P1 = 1
        P2 = 2

        def is_player1(self) -> bool:
            return self is GameState.Pid.P1

        def is_player2(self) -> bool:
            return self is GameState.Pid.P2

        def other(self) -> GameState.Pid:
            if self is GameState.Pid.P1:
                return GameState.Pid.P2
            elif self is GameState.Pid.P2:
                return GameState.Pid.P1
            else:
                raise Exception("Unknown situation of pid")

    def __init__(
        self,
        mode: md.Mode,
        phase: ph.Phase,
        round: int,
        active_player_id: GameState.Pid,
        player1: pl.PlayerState,
        player2: pl.PlayerState,
        effect_stack: EffectStack
    ):
        # REMINDER: don't forget to update factory when adding new fields
        self._mode = mode
        self._phase = phase
        self._round = round
        self._active_player_id = active_player_id
        self._player1 = player1
        self._player2 = player2
        self._effect_stack = effect_stack

        # checkers
        self._swap_checker = SwapChecker(self)

    @classmethod
    def from_default(cls):
        mode = md.DefaultMode()
        return cls(
            mode=mode,
            phase=mode.card_select_phase(),
            round=0,
            active_player_id=GameState.Pid.P1,
            player1=pl.PlayerState.examplePlayer(mode),
            player2=pl.PlayerState.examplePlayer(mode),
            effect_stack=EffectStack(()),
        )

    def factory(self):
        return GameStateFactory(self)

    def get_mode(self) -> md.Mode:
        return self._mode

    def get_phase(self) -> ph.Phase:
        return self._phase

    def get_round(self) -> int:
        return self._round

    def get_active_player_id(self) -> GameState.Pid:
        return self._active_player_id

    def get_effect_stack(self) -> EffectStack:
        return self._effect_stack

    def get_player1(self) -> pl.PlayerState:
        return self._player1

    def get_player2(self) -> pl.PlayerState:
        return self._player2

    def get_pid(self, player: pl.PlayerState) -> GameState.Pid:
        if player is self._player1:
            return self.Pid.P1
        elif player is self._player2:
            return self.Pid.P2
        else:
            raise Exception("player unknown")

    def get_player(self, player_id: GameState.Pid) -> pl.PlayerState:
        if player_id.is_player1():
            return self._player1
        elif player_id.is_player2():
            return self._player2
        else:
            raise Exception("player_id unknown")

    def get_other_player(self, player_id: GameState.Pid) -> pl.PlayerState:
        if player_id.is_player1():
            return self._player2
        elif player_id.is_player2():
            return self._player1
        else:
            raise Exception("player_id unknown")

    def swap_checker(self) -> SwapChecker:
        return self._swap_checker

    def belongs_to(self, object: Union[Character, int]) -> Optional[GameState.Pid]:
        """ int in object type is just place holder """
        if self._player1.is_mine(object):
            return GameState.Pid.P1
        elif self._player2.is_mine(object):
            return GameState.Pid.P2
        else:
            return None

    def get_target(self, target: StaticTarget) -> Optional[Union[Character, int]]:
        player = self.get_player(target.pid)
        if target.zone is Zone.CHARACTER:
            characters = player.get_characters()
            return characters.get_character(target.id)
        else:
            raise Exception("Not Implemented Yet")
        return None

    def get_character_target(self, target: StaticTarget) -> Optional[Character]:
        character = self.get_target(target)
        if not isinstance(character, Character):
            return None
        return cast(Character, character)

    def waiting_for(self) -> Optional[GameState.Pid]:
        return self._phase.waiting_for(self)

    def possible_actions(self, pid: GameState.Pid) -> dict[int, EventPre]:
        return self._phase.possible_actions(self)

    def step(self) -> GameState:
        return self._phase.step(self)

    def action_step(self, pid: GameState.Pid, action: PlayerAction) -> Optional[GameState]:
        """
        Returns None if the action is illegal or undefined
        """
        return self._phase.step_action(self, pid, action)

    def get_winner(self) -> Optional[GameState.Pid]:
        assert self.game_end()
        if self.get_player1().defeated():
            return GameState.Pid.P2
        elif self.get_player2().defeated():
            return GameState.Pid.P1
        else:
            return None

    def game_end(self) -> bool:
        return isinstance(self._phase, gep.GameEndPhase)

    def _all_unique_data(self) -> tuple:
        return (
            self._phase,
            self._round,
            self._active_player_id,
            self._player1,
            self._player2,
            self._effect_stack,
            self._mode,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GameState):
            return False
        return self._all_unique_data() == other._all_unique_data()

    def __hash__(self) -> int:
        return hash(self._all_unique_data())

    def __str__(self) -> str:
        from dgisim.src.helper.level_print import GamePrinter
        return GamePrinter.dict_game_printer(self.dict_str())

    def to_string(self, indent: int = 0) -> str:
        new_indent = indent + INDENT
        return level_print({
            "Mode": self._mode.to_string(new_indent),
            "Phase": self._phase.to_string(new_indent),
            "Round": level_print_single(str(self._round), new_indent),
            "Active Player": level_print_single(str(self._active_player_id), new_indent),
            "Player1": self._player1.to_string(new_indent),
            "Player2": self._player2.to_string(new_indent),
            "Effects": self._effect_stack.to_string(new_indent),
        }, indent)

    def dict_str(self) -> dict:
        return {
            "Mode": self._mode.dict_str(),
            "Phase": self._phase.dict_str(),
            "Round": str(self._round),
            "Active Player": str(self._active_player_id),
            "Player1": self._player1.dict_str(),
            "Player2": self._player2.dict_str(),
            "Effects": self._effect_stack.dict_str(),
        }


class GameStateFactory:
    def __init__(self, game_state: GameState):
        self._mode = game_state.get_mode()
        self._phase = game_state.get_phase()
        self._round = game_state.get_round()
        self._active_player = game_state.get_active_player_id()
        self._player1 = game_state.get_player1()
        self._player2 = game_state.get_player2()
        self._effect_stack = game_state.get_effect_stack()

    def mode(self, new_mode: md.Mode) -> GameStateFactory:
        self._mode = new_mode
        return self

    def phase(self, new_phase: ph.Phase) -> GameStateFactory:
        self._phase = new_phase
        return self

    def f_phase(self, f: Callable[[md.Mode], ph.Phase]) -> GameStateFactory:
        return self.phase(f(self._mode))

    def round(self, new_round: int) -> GameStateFactory:
        self._round = new_round
        return self

    def effect_stack(self, effect_stack: EffectStack) -> GameStateFactory:
        self._effect_stack = effect_stack
        return self

    def f_effect_stack(self, f: Callable[[EffectStack], EffectStack]) -> GameStateFactory:
        return self.effect_stack(f(self._effect_stack))

    def active_player_id(self, pid: GameState.Pid) -> GameStateFactory:
        self._active_player = pid
        return self

    def player1(self, new_player: pl.PlayerState) -> GameStateFactory:
        self._player1 = new_player
        return self

    def f_player1(self, f: Callable[[pl.PlayerState], pl.PlayerState]) -> GameStateFactory:
        return self.player1(f(self._player1))

    def player2(self, new_player: pl.PlayerState) -> GameStateFactory:
        self._player2 = new_player
        return self

    def f_player2(self, f: Callable[[pl.PlayerState], pl.PlayerState]) -> GameStateFactory:
        return self.player2(f(self._player2))

    def player(self, pid: GameState.Pid, new_player: pl.PlayerState) -> GameStateFactory:
        if pid is GameState.Pid.P1:
            return self.player1(new_player)
        elif pid is GameState.Pid.P2:
            return self.player2(new_player)
        else:
            raise Exception("player_id unknown")

    def f_player(self, pid: GameState.Pid, f: Callable[[pl.PlayerState], pl.PlayerState]) -> GameStateFactory:
        if pid is GameState.Pid.P1:
            return self.player1(f(self._player1))
        elif pid is GameState.Pid.P2:
            return self.player2(f(self._player2))
        else:
            raise Exception("player_id unknown")

    def other_player(self, pid: GameState.Pid, new_player: pl.PlayerState) -> GameStateFactory:
        if pid is GameState.Pid.P1:
            return self.player2(new_player)
        elif pid is GameState.Pid.P2:
            return self.player1(new_player)
        else:
            raise Exception("player_id unknown")

    def f_other_player(self, pid: GameState.Pid, f: Callable[[pl.PlayerState], pl.PlayerState]) -> GameStateFactory:
        if pid is GameState.Pid.P1:
            return self.player2(f(self._player2))
        elif pid is GameState.Pid.P2:
            return self.player1(f(self._player1))
        else:
            raise Exception("player_id unknown")

    def build(self) -> GameState:
        return GameState(
            mode=self._mode,
            phase=self._phase,
            round=self._round,
            active_player_id=self._active_player,
            effect_stack=self._effect_stack,
            player1=self._player1,
            player2=self._player2,
        )


class SwapChecker:
    def __init__(self, game_state: GameState) -> None:
        self._game_state = game_state

    def swap_speed(
            self,
            pid: GameState.Pid,
            char_id: int,
            death_swap: bool = False,
    ) -> None | EventSpeed:
        game_state = self._game_state
        selected_char = game_state.get_player(pid).get_characters().get_character(char_id)
        active_character_id = game_state.get_player(pid).get_characters().get_active_character_id()
        if selected_char is None \
                or selected_char.defeated() \
                or selected_char.get_id() == active_character_id:
            return None
        # Check Death Swap
        if death_swap:
            effect_stack = game_state.get_effect_stack()
            if effect_stack.is_not_empty() \
                    and isinstance(effect_stack.peek(), eft.DeathSwapPhaseStartEffect):
                return EventSpeed.FAST_ACTION
            else:
                return None

        # Check if player can afford Normal Swap
        from dgisim.src.status.status_processing import StatusProcessing
        # ppd is preprocessed
        _, swap_action = StatusProcessing.preprocess_by_all_statuses(
            game_state=game_state,
            pid=pid,
            item=GameEvent(
                target=eft.StaticTarget(
                    pid=pid,
                    zone=eft.Zone.CHARACTER,
                    id=char_id,
                ),
                event_type=EventType.SWAP,
                event_speed=game_state.get_mode().swap_speed(),
                dices_cost=game_state.get_mode().swap_cost(),
            ),
            pp_type=stt.Status.PPType.SWAP,
        )
        assert isinstance(swap_action, GameEvent)
        if game_state.get_player(pid).get_dices().loosely_satisfy(swap_action.dices_cost):
            return swap_action.event_speed
        else:
            return None

    def valid_action(
            self,
            pid: GameState.Pid,
            action: act.SwapAction | act.DeathSwapAction,
    ) -> None | tuple[GameState, EventSpeed]:
        """
        Return None if the action is invalid,
        otherwise return the GameState after preprocessing the swap event.
        """
        game_state = self._game_state
        selected_char = game_state.get_player(
            pid
        ).get_characters().get_character(action.selected_character_id)
        active_character_id = game_state.get_player(pid).get_characters().get_active_character_id()
        if selected_char is None \
                or selected_char.defeated() \
                or selected_char.get_id() == active_character_id:
            return None
        if isinstance(action, act.DeathSwapAction):
            swap_speed = self.swap_speed(
                pid=pid,
                char_id=action.selected_character_id,
                death_swap=True,
            )
            return case_val(
                swap_speed is not None,
                (game_state, EventSpeed.FAST_ACTION),
                None,
            )
        elif isinstance(action, act.SwapAction):
            from dgisim.src.status.status_processing import StatusProcessing
            new_game_state, swap_action = StatusProcessing.preprocess_by_all_statuses(
                game_state=game_state,
                pid=pid,
                item=GameEvent(
                    target=eft.StaticTarget(
                        pid=pid,
                        zone=eft.Zone.CHARACTER,
                        id=action.selected_character_id,
                    ),
                    event_type=EventType.SWAP,
                    event_speed=game_state.get_mode().swap_speed(),
                    dices_cost=game_state.get_mode().swap_cost(),
                ),
                pp_type=stt.Status.PPType.SWAP,
            )
            assert isinstance(swap_action, GameEvent)
            instruction_dices = action.instruction.dices
            player_dices = game_state.get_player(pid).get_dices()
            return case_val(
                (player_dices - instruction_dices).is_legal()
                and instruction_dices.just_satisfy(swap_action.dices_cost),
                (new_game_state, swap_action.event_speed),
                None
            )
        raise Exception("action ({action}) is not expected to be passed in")


if __name__ == "__main__":
    initial_state = GameState.from_default()
    pid = initial_state.waiting_for()
    assert pid is None
    state = initial_state.step()
    pass
