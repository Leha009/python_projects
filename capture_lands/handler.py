import random
from PyQt6.QtCore import pyqtSignal, QTimer, QObject

from map import CellCoords, Map

TICK_MS = 1000

class GameHandler(QObject):
    # signals
    tick = pyqtSignal()
    # who, what captured
    captured = pyqtSignal(int, CellCoords)
    # who, source, target, how many
    troops_moved = pyqtSignal(int, CellCoords, CellCoords, int)

    # tick timer
    _tick_timer: QTimer

    _players: list[int]
    _map: Map
    _ticks: int
    _bots: list

    def __init__(self, map: Map, num_of_players: int, num_of_bots: int) -> None:
        """
        Initializes the GameHandler with the specified map and number of players.

        Args:
            map (Map): The map instance for the game.
            num_of_players (int): The total number of players in the game.

        Sets up players and bots, initializes the game state, and configures the tick timer.
        """
        from bot import RandomCaptureBot
        if num_of_bots > num_of_players:
            raise ValueError("Cannot have more bots than players.")

        super().__init__()
        self._map = map
        self._ticks = 0
        self._players = [i for i in range(1, num_of_players+1)]
        self._bots = [
            RandomCaptureBot(bot_id, self)
            for bot_id in range(num_of_players-num_of_bots+1, num_of_players+1)
        ]

        self.init_startup()

        self._tick_timer = QTimer(self)
        self._tick_timer.setInterval(TICK_MS)
        self._tick_timer.setSingleShot(False)
        self._tick_timer.timeout.connect(self.next_tick)

    def init_startup(self) -> None:
        """
        Initializes the starting positions for each player on the map.

        Randomly assigns a cell on the map to each player, setting them as the owner
        and resetting the ticks to fill for that cell to zero.
        """
        for player in self._players:
            x = random.randint(0, self._map.width - 1)
            y = random.randint(0, self._map.height - 1)
            cell = self._map.get_cell(CellCoords(x, y))
            cell.player_owner = player
            cell.ticks_to_fill = 0
            self.captured.emit(player, CellCoords(x, y))

    def get_map(self) -> Map:
        """
        Returns the map instance used for the game.

        Returns:
            Map: The map instance for the game.
        """
        return self._map

    def move_troops(
        self,
        who_move: int,
        target_coords: CellCoords,
        source_coords: CellCoords
    ) -> None:
        """
        Move troops from the source cell to the target cell if possible.

        Only moves troops if the game is not stopped, the target cell is adjacent
        to the source cell, the source cell is owned by the player, and the target
        cell can be captured. If the target cell is owned by the same player, just
        adds the troops to the target cell. If the target cell is not owned by the
        same player, removes the troops from the target cell and captures it if
        the player has more troops than the target cell.

        Emits the `troops_moved` signal with the player who moved, source and target
        coordinates, and the number of troops moved. If the target cell was captured,
        also emits the `captured` signal with the player who captured the cell and
        the target coordinates.

        Args:
            who_move (int): The player who is moving troops.
            target_coords (CellCoords): The coordinates of the cell to move troops to.
            source_coords (CellCoords): The coordinates of the cell to move troops from.
        """
        if self.is_stopped() or not target_coords.is_nearby(source_coords):
            return

        cell_source = self._map.get_cell(source_coords)
        if cell_source.player_owner != who_move:
            return

        cell_target = self._map.get_cell(target_coords)
        source_troops = cell_source.current_capacity

        if not cell_target.can_be_captured:
            return

        if cell_target.player_owner == cell_source.player_owner:
            cell_target.add(source_troops)
            cell_source.remove(source_troops)
            self.troops_moved.emit(
                cell_source.player_owner, source_coords, target_coords, source_troops
            )
            return

        target_troops = cell_target.current_capacity
        cell_target.remove(source_troops)
        if target_troops < source_troops:
            cell_target.add(source_troops - target_troops)
            cell_target.player_owner = cell_source.player_owner
            self.captured.emit(cell_target.player_owner, target_coords)

        cell_source.remove(source_troops)
        self.troops_moved.emit(
            cell_source.player_owner, source_coords, target_coords, source_troops
        )

    def next_tick(self) -> None:
        """
        Updates the capacity of each cell on the map and emits the `tick` signal.

        This method should be called once per tick of the game. It updates the
        capacity of each cell based on the current game state and emits the
        `tick` signal to notify any connected slots that the game state has
        changed.
        """
        self._ticks += 1
        for y in range(self._map.height):
            for x in range(self._map.width):
                cell = self._map.get_cell(CellCoords(x, y))
                cell.update_capacity()

        self.tick.emit()

    def get_ticks(self) -> int:
        """
        Returns the number of ticks since the game started.

        Returns:
            int: The number of ticks since the game started.
        """
        return self._ticks

    def is_stopped(self) -> bool:
        """
        Checks if the game is stopped.

        Returns:
            bool: True if the game is stopped (i.e., the tick timer is not active),
                  False otherwise.
        """
        return not self._tick_timer.isActive()

    def stop(self) -> None:
        """
        Stops the game.

        Stops the game by stopping the tick timer. This has the effect of
        freezing the game state, so no more ticks will occur until the game
        is resumed.
        """
        self._tick_timer.stop()

    def resume(self) -> None:
        """
        Resumes the game.

        Resumes the game by starting the tick timer, so the game state will
        once again change every tick period.
        """
        self._tick_timer.start()
