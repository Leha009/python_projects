from enum import Enum
import random
from PyQt6.QtCore import pyqtSignal, QTimer, QObject

from map import CellCoords, Map

TICK_MS = 1000

class GameStatus(Enum):
    ACTIVE = 0
    PAUSED = 1
    END = 2

class GameHandler(QObject):
    # signals
    tick = pyqtSignal()
    # who, what captured
    captured = pyqtSignal(int, CellCoords)
    # who, source, target, how many
    troops_moved = pyqtSignal(int, CellCoords, CellCoords, int)
    # eliminated player id
    eliminated = pyqtSignal(int)
    # new status
    game_state_changed = pyqtSignal(GameStatus)

    # tick timer
    _tick_timer: QTimer

    _players_cells: dict[int, int]
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
        from bot import RandomCaptureBot, DefensiveBot, AggressiveBot, AggressiveAllAdjacentBot
        if num_of_bots > num_of_players:
            raise ValueError("Cannot have more bots than players.")

        super().__init__()
        self._map = map
        self._ticks = 0
        self._players_cells = {i: 0 for i in range(num_of_players+1)}
        self._players = [i for i in range(1, num_of_players+1)]
        bots = [AggressiveAllAdjacentBot]
        self._bots = [
            random.choice(bots)(bot_id, self)
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
            self._players_cells[player] += 1

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
        attack_troops = int(source_troops * random.uniform(0.75, 1.25))

        if not cell_target.can_be_captured:
            return

        if cell_target.player_owner == cell_source.player_owner:
            cell_target.add(attack_troops)
            cell_source.remove(source_troops)
            self.troops_moved.emit(
                cell_source.player_owner, source_coords, target_coords, attack_troops
            )
            return

        target_troops = cell_target.current_capacity
        cell_target.remove(attack_troops)
        if target_troops < attack_troops:
            cell_target.add(attack_troops - target_troops)
            self.capture_cell(cell_source.player_owner, target_coords)

        cell_source.remove(source_troops)
        self.troops_moved.emit(
            cell_source.player_owner, source_coords, target_coords, attack_troops
        )

    def capture_cell(self, new_owner_id: int, coords: CellCoords) -> None:
        """
        Captures a cell for a specified player.

        This function updates the owner of the cell at the given coordinates
        to the specified player. It adjusts the count of cells owned by the
        previous owner and the new owner. If the previous owner has no more
        cells, they are eliminated from the game.

        Args:
            player (int): The ID of the player capturing the cell.
            coords (CellCoords): The coordinates of the cell being captured.
        """
        cell = self._map.get_cell(coords)
        old_owner = cell.player_owner
        cell.player_owner = new_owner_id
        self._players_cells[old_owner] -= 1
        self._players_cells[new_owner_id] += 1
        self.captured.emit(new_owner_id, coords)
        if self._players_cells[old_owner] == 0:
            self.eliminate_player(old_owner)

    def eliminate_player(self, player: int) -> None:
        self._players.remove(player)
        self._players_cells.pop(player)
        self.eliminated.emit(player)
        #print(f"Player {player} eliminated.")
        print(f"Bot #{player} {self._bots[player-1].__class__.__name__} eliminated.")
        if len(self._players) < 2:
            player = self._players[0]
            print(f"Bot #{player} {self._bots[player-1].__class__.__name__} won.")
            self.end_game()

    def alive_players_count(self) -> int:
        """
        Returns the number of players that are still alive in the game.

        Returns:
            int: The number of alive players.
        """
        return len(self._players)

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

    def pause(self) -> None:
        """
        Stops the game.

        Stops the game by stopping the tick timer. This has the effect of
        freezing the game state, so no more ticks will occur until the game
        is resumed.
        """
        self._tick_timer.stop()
        self.game_state_changed.emit(GameStatus.PAUSED)

    def resume(self) -> None:
        """
        Resumes the game.

        Resumes the game by starting the tick timer, so the game state will
        once again change every tick period.
        """
        self._tick_timer.start()
        self.game_state_changed.emit(GameStatus.ACTIVE)

    def end_game(self) -> None:
        """
        Ends the game.

        Ends the game by stopping the tick timer, so no more ticks will occur
        until the game is started again.
        """
        self._tick_timer.stop()
        self.game_state_changed.emit(GameStatus.END)
