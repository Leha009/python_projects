import random
from PyQt6.QtCore import pyqtSignal, QTimer, QObject

from bot import Bot, RandomCaptureBot
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
    _bots: list[Bot]

    def __init__(self, map: Map, num_of_players: int) -> None:
        """
        Initialize the handler with a map of the specified size
        """
        super().__init__()
        self._map = map
        self._ticks = 0
        self._players = [i for i in range(1, num_of_players+1)]
        self._bots = [RandomCaptureBot(map) for _ in range(num_of_players-1)]

        self.init_startup()

        self._tick_timer = QTimer(self)
        self._tick_timer.setInterval(TICK_MS)
        self._tick_timer.setSingleShot(False)
        self._tick_timer.timeout.connect(self.next_tick)

    def init_startup(self) -> None:
        for player in self._players:
            x = random.randint(0, self._map.width - 1)
            y = random.randint(0, self._map.height - 1)
            cell = self._map.get_cell(CellCoords(x, y))
            cell.player_owner = player
            cell.ticks_to_fill = 0

    def get_map(self) -> Map:
        return self._map

    def move_troops(
        self,
        who_move: int,
        target_coords: CellCoords,
        source_coords: CellCoords
    ) -> None:
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
        self._ticks += 1
        for y in range(self._map.height):
            for x in range(self._map.width):
                cell = self._map.get_cell(CellCoords(x, y))
                cell.update_capacity()

        self.tick.emit()

    def get_ticks(self) -> int:
        return self._ticks

    def is_stopped(self) -> bool:
        return not self._tick_timer.isActive()

    def stop(self) -> None:
        self._tick_timer.stop()

    def resume(self) -> None:
        self._tick_timer.start()
