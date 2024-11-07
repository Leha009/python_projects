from abc import ABC, abstractmethod
import random
from handler import GameHandler
from map import CellCoords

class Bot(ABC):
    _game_handler: GameHandler
    _id: int

    def __init__(self, bot_id: int, handler: GameHandler) -> None:
        self._id = bot_id
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

    def __init__(self, bot_id: int, handler: GameHandler) -> None:
        super().__init__(bot_id, handler)
        self._my_cells: list[CellCoords] = list()

    def tick(self) -> None:
        if len(self._my_cells) == 0:
            return

        cell_coords: CellCoords = random.choice(self._my_cells)
        cell = self._game_handler.get_map().get_cell(cell_coords)
        if cell.current_capacity == 0:
            return

        dx, dy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        target_coords = CellCoords(cell_coords.x + dx, cell_coords.y + dy)
        if not self._game_handler.get_map().is_cell_valid(target_coords):
            return

        self._game_handler.move_troops(self._id, target_coords, cell_coords)

    def on_captured(self, player_id: int, cell_coords: CellCoords) -> None:
        if cell_coords in self._my_cells:
            self._my_cells.remove(cell_coords)
        elif player_id == self._id:
            self._my_cells.append(cell_coords)

    def on_troops_moved(
        self,
        player_id: int,
        from_cell: CellCoords,
        to_cell: CellCoords,
        num_of_troops: int
    ) -> None:
        pass

class DefensiveBot(Bot):
    def __init__(self, bot_id: int, handler: GameHandler) -> None:
        super().__init__(bot_id, handler)
        self._my_cells: list[CellCoords] = list()

    def tick(self) -> None:
        for cell_coords in self._my_cells:
            cell = self._game_handler.get_map().get_cell(cell_coords)
            if cell.current_capacity == 0:
                continue

            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                target_coords = CellCoords(cell_coords.x + dx, cell_coords.y + dy)
                if not self._game_handler.get_map().is_cell_valid(target_coords):
                    continue

                target_cell = self._game_handler.get_map().get_cell(target_coords)
                if target_cell.player_owner != self._id and target_cell.current_capacity < cell.current_capacity:
                    self._game_handler.move_troops(self._id, target_coords, cell_coords)
                    break

    def on_captured(self, player_id: int, cell_coords: CellCoords) -> None:
        if cell_coords in self._my_cells:
            self._my_cells.remove(cell_coords)
        elif player_id == self._id:
            self._my_cells.append(cell_coords)

    def on_troops_moved(
        self,
        player_id: int,
        from_cell: CellCoords,
        to_cell: CellCoords,
        num_of_troops: int
    ) -> None:
        pass

class AggressiveBot(Bot):
    def __init__(self, bot_id: int, handler: GameHandler) -> None:
        super().__init__(bot_id, handler)
        self._my_cells: list[CellCoords] = list()

    def tick(self) -> None:
        for cell_coords in self._my_cells:
            cell = self._game_handler.get_map().get_cell(cell_coords)
            if cell.current_capacity == 0:
                continue

            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                target_coords = CellCoords(cell_coords.x + dx, cell_coords.y + dy)
                if not self._game_handler.get_map().is_cell_valid(target_coords):
                    continue

                target_cell = self._game_handler.get_map().get_cell(target_coords)
                if target_cell.player_owner != self._id and target_cell.current_capacity < cell.current_capacity:
                    self._game_handler.move_troops(self._id, target_coords, cell_coords)
                    break

    def on_captured(self, player_id: int, cell_coords: CellCoords) -> None:
        if cell_coords in self._my_cells:
            self._my_cells.remove(cell_coords)
        elif player_id == self._id:
            self._my_cells.append(cell_coords)

    def on_troops_moved(
        self,
        player_id: int,
        from_cell: CellCoords,
        to_cell: CellCoords,
        num_of_troops: int
    ) -> None:
        pass
