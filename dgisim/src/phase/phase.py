from __future__ import annotations
from typing import Optional

import dgisim.src.state.game as gm


class Phase:
    def run(self, game_state: gm.GameState) -> gm.GameState:
        raise Exception("Not Overriden")

    def run_action(self, game_state: gm.GameState, pid: gm.GameState.pid, action) -> gm.GameState:
        raise Exception("Not Overriden")

    def waiting_for(self, game_state: gm.GameState) -> Optional[gm.GameState.pid]:
        raise Exception("Not Overriden")

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Phase)

    def __hash__(self) -> int:
        return hash(self.__class__.__name__)
