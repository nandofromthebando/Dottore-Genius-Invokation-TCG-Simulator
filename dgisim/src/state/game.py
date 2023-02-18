from __future__ import annotations
from typing import Optional
from enum import Enum

import dgisim.src.mode.mode as md
import dgisim.src.phase.phase as ph
import dgisim.src.state.player as pl
from dgisim.src.helper.level_print import level_print, level_print_single, INDENT


class GameState:
    class pid(Enum):
        P1 = 1
        P2 = 2

    ROUND_LIMIT = 15
    # CARD_SELECT_PHASE = "Card Selection Phase"
    # STARTING_HAND_SELECT_PHASE = "Starting Hand Selection Phase"
    # ROLL_PHASE = "Roll Phase"
    # ACTION_PHASE = "Action Phase"
    # END_PHASE = "End Phase"
    # GAME_END_PHASE = "Game End Phase"

    def __init__(
            self,
            phase: ph.Phase,
            round: int,
            mode: md.Mode,
            player1: pl.PlayerState,
            player2: pl.PlayerState,
        ):
        # REMINDER: don't forget to update factory when adding new fields
        self._phase = phase
        self._round = round
        self._active_player = self.pid.P1
        self._player1 = player1
        self._player2 = player2
        self._mode = mode

    @classmethod
    def from_default(cls):
        return cls(
            md.DefaultMode().card_select_phase(),
            0,
            md.DefaultMode(),
            pl.PlayerState.examplePlayer(),
            pl.PlayerState.examplePlayer()
        )

    def factory(self):
        return GameStateFactory(self)

    def get_phase(self) -> ph.Phase:
        return self._phase

    def get_round(self) -> int:
        return self._round

    def get_active_player(self) -> GameState.pid:
        return self._active_player

    def get_mode(self) -> md.Mode:
        return self._mode

    def get_player1(self) -> pl.PlayerState:
        return self._player1

    def get_player2(self) -> pl.PlayerState:
        return self._player2

    def get_pid(self, player: pl.PlayerState) -> GameState.pid:
        if player is self._player1:
            return self.pid.P1
        elif player is self._player2:
            return self.pid.P2
        else:
            raise Exception("player unknown")

    def get_player(self, player_id: GameState.pid) -> pl.PlayerState:
        if player_id is self.pid.P1:
            return self._player1
        elif player_id is self.pid.P2:
            return self._player2
        else:
            raise Exception("player_id unknown")

    def get_other_player(self, player_id: GameState.pid) -> pl.PlayerState:
        if player_id is self.pid.P1:
            return self._player2
        elif player_id is self.pid.P2:
            return self._player1
        else:
            raise Exception("player_id unknown")

    def waiting_for(self) -> Optional[GameState.pid]:
        return self._phase.waiting_for(self)

    def run(self) -> GameState:
        return self._phase.run(self)

    def run_action(self, pid, action) -> GameState:
        return self._phase.run_action(self, pid, action)

    def get_winner(self) -> Optional[GameState.pid]:
        if self._round > self.ROUND_LIMIT:
            return None
        # TODO
        # based on player's health
        return None

    def game_end(self) -> bool:
        if self._round > self.ROUND_LIMIT:
            return True
        # TODO
        # check player's health
        return False

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GameState):
            return False
        return self._phase == other._phase \
            and self._round == other._round \
            and self._active_player == other._active_player \
            and self._player1 == other._player1 \
            and self._player2 == other._player2 \
            and self._mode == other._mode

    def __hash__(self) -> int:
        return hash((
            self._phase,
            self._round,
            self._player1,
            self._player2,
            self._mode,
        ))

    def __str__(self) -> str:
        return self.to_string(0)

    def to_string(self, indent: int = 0) -> str:
        new_indent = indent + INDENT
        return level_print({
            "Mode": self._mode.to_string(new_indent),
            "Phase": self._phase.to_string(new_indent),
            "Round": level_print_single(str(self._round), new_indent),
            "Active Player": level_print_single(str(self._active_player), new_indent),
            "Player1": self._player1.to_string(new_indent),
            "Player2": self._player2.to_string(new_indent),
        }, indent)


class GameStateFactory:
    def __init__(self, game_state: GameState):
        self._phase = game_state.get_phase()
        self._round = game_state.get_round()
        self._active_player = game_state.get_active_player()
        self._player1 = game_state.get_player1()
        self._player2 = game_state.get_player2()
        self._mode = game_state.get_mode()

    def phase(self, new_phase: ph.Phase) -> GameStateFactory:
        self._phase = new_phase
        return self

    def round(self, new_round: int) -> GameStateFactory:
        self._round = new_round
        return self

    def mode(self, new_mode: md.Mode) -> GameStateFactory:
        self._mode = new_mode
        return self

    def active_player(self, pid: GameState.pid) -> GameStateFactory:
        self._active_player = pid
        return self

    def player1(self, new_player: pl.PlayerState) -> GameStateFactory:
        self._player1 = new_player
        return self

    def player2(self, new_player: pl.PlayerState) -> GameStateFactory:
        self._player2 = new_player
        return self

    def player(self, pid: GameState.pid, new_player: pl.PlayerState) -> GameStateFactory:
        if pid is GameState.pid.P1:
            self._player1 = new_player
        elif pid is GameState.pid.P2:
            self._player2 = new_player
        else:
            raise Exception("player_id unknown")
        return self

    def otherPlayer(self, pid: GameState.pid, new_player: pl.PlayerState) -> GameStateFactory:
        if pid is GameState.pid.P1:
            self._player2 = new_player
        elif pid is GameState.pid.P2:
            self._player1 = new_player
        else:
            raise Exception("player_id unknown")
        return self

    def build(self) -> GameState:
        return GameState(
            phase=self._phase,
            round=self._round,
            mode=self._mode,
            player1=self._player1,
            player2=self._player2
        )


if __name__ == "__main__":
    initial_state = GameState.from_default()
    pid = initial_state.waiting_for()
    assert pid is None
    state = initial_state.run()
    pass
