from __future__ import annotations
from typing import Dict, Tuple

from dgisim.src.card.card import Card
from dgisim.src.helper.hashable_dict import HashableDict
from dgisim.src.helper.level_print import level_print, INDENT, level_print_single


class Cards:
    def __init__(self, mapping: Dict[Card, int]) -> None:
        self._cards = HashableDict(mapping)

    @classmethod
    def empty(cls) -> Cards:
        return Cards({})

    def new_with(self, cards: Dict[Card, int]) -> Cards:
        return Cards(self._cards | cards)

    def pick_random_cards(self, num: int) -> Tuple[Dict[Card, int], Dict[Card, int]]:
        # TODO
        import random
        tmp = random.sample(list(self._cards.keys()), counts=self._cards.values(), k=num)
        return ({}, {})

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Cards):
            return False
        return self._cards == other._cards

    def __hash__(self) -> int:
        return hash(self._cards)

    def __str__(self) -> str:
        return self.to_string(0)

    def to_string(self, indent: int = 0):
        existing_cards = dict([
            (str(card), level_print_single(str(num), indent + INDENT))
            for card, num in self._cards.items()
            if num != 0
        ])
        return level_print(existing_cards, indent)
