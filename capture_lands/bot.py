from abc import ABC, abstractmethod
from handler import GameHandler
from map import CellCoords

class Bot(ABC):
    _game_handler: GameHandler

    def __init__(self, handler: GameHandler) -> None:
        self._game_handler = handler
        self._game_handler.tick.connect(self.tick)
        self._game_handler.troops_moved.connect(self.on_troops_moved)
        self._game_handler.captured.connect(self.on_captured)

    @abstractmethod
    def tick(self) -> None:
        """
        Called every time a new game tick happens.

        The bot should use this method to decide what to do next.
        """

    @abstractmethod
    def on_troops_moved(
        self,
        player_id: int,
        from_cell: CellCoords,
        to_cell: CellCoords,
        num_of_troops: int
    ) -> None:
        """Called when a player moves troops between two cells.

        Args:
            player_id (int): The ID of the player who moved the troops.
            from_cell (CellCoords): The coordinates of the cell where the troops were moved from.
            to_cell (CellCoords): The coordinates of the cell where the troops were moved to.
            num_of_troops (int): The number of troops that were moved.
        """

    @abstractmethod
    def on_captured(self, player_id: int, cell: CellCoords) -> None:
        """Called when a player captures a cell.

        Args:
            player_id (int): The ID of the player who captured the cell.
            cell (CellCoords): The coordinates of the captured cell.
        """

class RandomCaptureBot(Bot):
    def tick(self) -> None:
        pass
