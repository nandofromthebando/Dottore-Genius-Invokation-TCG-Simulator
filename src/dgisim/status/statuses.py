from __future__ import annotations
from typing import Iterator, Optional, TYPE_CHECKING, TypeVar
from typing_extensions import Self

from ..status import status as stt

from ..helper.quality_of_life import just


_U = TypeVar('_U')


class Statuses:
    def __init__(self, statuses: tuple[stt.Status, ...]):
        self._statuses = statuses

    def update_status(self, incoming_status: stt.Status, override: bool = False) -> Self:
        """
        Replaces existing status of the same type with the new_status,
        or append the new_status to the end of current statuses
        """
        cls = type(self)
        statuses = list(self._statuses)
        for i, status in enumerate(statuses):
            if type(status) is not type(incoming_status):
                continue
            new_status: Optional[stt.Status]
            if override:
                new_status = incoming_status
            else:
                new_status = status.update(incoming_status)
            if status == new_status:
                return self
            if new_status is None:
                return self.remove(type(status))
            statuses[i] = new_status
            return cls(tuple(statuses))
        statuses.append(incoming_status)
        return cls(tuple(statuses))

    def contains(self, status: type[stt.Status]) -> bool:
        return any(type(b) is status for b in self._statuses)

    def find(self, status: type[stt.Status]) -> Optional[stt.Status]:
        return next((bf for bf in self._statuses if type(bf) is status), None)

    def just_find(self, status: type[_U]) -> _U:
        """ _U should be a subclass of type[Status] """
        assert issubclass(status, stt.Status)
        found_status = just(self.find(status))
        assert isinstance(found_status, status)
        return found_status  # type: ignore

    def remove(self, status: type[stt.Status]) -> Self:
        return type(self)(tuple(
            filter(lambda bf: type(bf) != status, self._statuses)
        ))

    def get_statuses(self) -> tuple[stt.Status, ...]:
        return self._statuses

    def __iter__(self) -> Iterator[stt.Status]:
        return iter(self._statuses)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Statuses):
            return False
        return self is other or self == other

    def __hash__(self) -> int:
        return hash(self._statuses)

    def __str__(self) -> str:
        return '[' + ', '.join(map(str, self._statuses)) + ']'

    def dict_str(self) -> list:
        return [
            str(status)
            for status in self._statuses
        ]


class EquipmentStatuses(Statuses):
    pass


class OrderedStatuses(Statuses):
    pass


class TalentStatuses(Statuses):
    pass
