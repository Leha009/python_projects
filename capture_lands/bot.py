from abc import ABC, abstractmethod
from map import Map


class Bot(ABC):
    _map: Map

    def __init__(self, map: Map) -> None:
        self._map = map

    @abstractmethod
    def tick(self) -> None:
        pass

class RandomCaptureBot(Bot):
    def tick(self) -> None:
        pass
