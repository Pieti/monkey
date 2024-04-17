from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from monkey.mobj import MonkeyObject


class Environment:
    def __init__(self, outer: Optional["Environment"] = None):
        self.store: dict[str, "MonkeyObject"] = {}
        self.outer = outer

    def get(self, str) -> Optional["MonkeyObject"]:
        if obj := self.store.get(str, None):
            return obj
        if self.outer:
            return self.outer.get(str)
        return None

    def put(self, name: str, obj: "MonkeyObject") -> None:
        self.store[name] = obj
