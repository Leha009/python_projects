from __future__ import annotations
from collections import namedtuple

class Cell():
    _max_capacity = 0
    _current_capacity = 0
    _ticks_to_fill = 0
    _ticks_left = 0
    _can_be_captured = False

    def __init__(self, max_capacity, current_capacity = 0, ticks_to_fill = 2) -> None:
        self._max_capacity = max_capacity
        self._current_capacity = current_capacity
        self._ticks_to_fill = ticks_to_fill
        self._ticks_left = self._ticks_to_fill
        self._can_be_captured = True
        self._player_owner = 0

    def update_capacity(self) -> None:
        if self._ticks_left > 0:
            self._ticks_left -= 1
            return

        if self._current_capacity < self.max_capacity:
            self._current_capacity += 1
        elif self._current_capacity > self.max_capacity:
            self._current_capacity -= 1

        self._ticks_left = self._ticks_to_fill

    def add(self, amount) -> None:
        self._current_capacity += amount

    def remove(self, amount) -> int:
        if self._current_capacity < amount:
            amount = self._current_capacity
            self._current_capacity = 0
        else:
            self._current_capacity -= amount

        return amount

    @property
    def current_capacity(self) -> int:
        return self._current_capacity

    @property
    def max_capacity(self) -> int:
        return self._max_capacity

    @property
    def ticks_to_fill(self) -> int:
        return self._ticks_to_fill

    @ticks_to_fill.setter
    def ticks_to_fill(self, value: int) -> None:
        self._ticks_to_fill = value
        if self._ticks_left > self._ticks_to_fill:
            self._ticks_left = self._ticks_to_fill

    @property
    def player_owner(self) -> int:
        return self._player_owner

    @player_owner.setter
    def player_owner(self, value: int) -> None:
        self._player_owner = value

    def is_owned(self) -> bool:
        return self._player_owner != 0

    @property
    def can_be_captured(self) -> bool:
        return self._can_be_captured

    @can_be_captured.setter
    def can_be_captured(self, value: bool) -> None:
        self._can_be_captured = value

    def __str__(self) -> str:
        if self.can_be_captured:
            return f"{self._current_capacity}/{self.max_capacity}"

        return "X"

class CellCoords(namedtuple("CellCoords", ["x", "y"])):
    def is_nearby(self, coords: CellCoords) -> bool:
        return abs(self.x - coords.x) <= 1 and abs(self.y - coords.y) <= 1

class Map():
    _cells: list

    def __init__(self, width, height) -> None:
        self._cells = [[Cell(10) for _ in range(width)] for _ in range(height)]

    def get_cell(self, coords: CellCoords) -> Cell:
        if coords.x < 0 or coords.x >= len(self._cells[0]):
            raise ValueError("x is out of range")
        if coords.y < 0 or coords.y >= len(self._cells):
            raise ValueError("y is out of range")

        return self._cells[coords.y][coords.x]

    @property
    def height(self) -> int:
        return len(self._cells)

    @property
    def width(self) -> int:
        return len(self._cells[0])
