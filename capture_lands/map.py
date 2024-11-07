from __future__ import annotations
from collections import namedtuple
import random

class Cell():
    _max_capacity = 0
    _current_capacity = 0
    _ticks_to_fill = 0
    _ticks_left = 0
    _can_be_captured = False

    def __init__(self, max_capacity, current_capacity = 0, ticks_to_fill = 2) -> None:
        """
        Initializes the cell with the given maximum capacity, current capacity,
        and time to fill the cell.

        Args:
            max_capacity (int): The maximum capacity of the cell.
            current_capacity (int, optional): The current capacity of the cell.
                Defaults to 0.
            ticks_to_fill (int, optional): The time to fill the cell. Defaults to
                2.
        """
        self._max_capacity = max_capacity
        self._current_capacity = current_capacity
        self._ticks_to_fill = ticks_to_fill
        self._ticks_left = self._ticks_to_fill
        self._can_be_captured = True
        self._player_owner = 0

    def update_capacity(self) -> None:
        """
        Updates the cell's capacity.

        Increases the cell's capacity by 1 if the current capacity is less
        than the maximum capacity. Decreases the capacity by 1 if the current
        capacity is greater than the maximum capacity. Leaves the capacity
        unchanged if the current capacity is equal to the maximum capacity.

        Resets the ticks left for the next update to the ticks required to
        fill the cell.
        """
        if self._current_capacity > self.max_capacity:
            self._current_capacity -= 1

        if self._ticks_left > 0:
            self._ticks_left -= 1
            return

        if self._current_capacity < self.max_capacity:
            self._current_capacity += 1

        self._ticks_left = self._ticks_to_fill

    def add(self, amount) -> None:
        """
        Increases the cell's current capacity by the specified amount.

        Args:
            amount (int): The amount by which to increase the current capacity.
        """
        self._current_capacity += amount

    def remove(self, amount) -> int:
        """
        Removes the specified amount from the cell's current capacity.

        If the amount to be removed is greater than the current capacity,
        sets the current capacity to zero and returns the actual amount removed.

        Args:
            amount (int): The amount to remove from the current capacity.

        Returns:
            int: The actual amount removed from the current capacity, which may
                be less than the specified amount if the current capacity is less.
        """
        if self._current_capacity < amount:
            amount = self._current_capacity
            self._current_capacity = 0
        else:
            self._current_capacity -= amount

        return amount

    @property
    def current_capacity(self) -> int:
        """
        The current capacity of the cell.

        Returns:
            int: The current capacity.
        """
        return self._current_capacity

    @property
    def max_capacity(self) -> int:
        """
        The maximum capacity of the cell.

        Returns:
            int: The maximum capacity.
        """
        return self._max_capacity

    @property
    def ticks_to_fill(self) -> int:
        """
        The number of ticks required to fill the cell.

        Returns:
            int: The number of ticks.
        """
        return self._ticks_to_fill

    @ticks_to_fill.setter
    def ticks_to_fill(self, value: int) -> None:
        """
        Sets the number of ticks required to fill the cell.

        If the current number of ticks left to fill the cell is greater than
        the new number of ticks to fill the cell, sets the current number of
        ticks left to fill the cell to the new number of ticks to fill the
        cell.

        Args:
            value (int): The new number of ticks required to fill the cell.
        """
        self._ticks_to_fill = value
        if self._ticks_left > self._ticks_to_fill:
            self._ticks_left = self._ticks_to_fill

    @property
    def player_owner(self) -> int:
        """
        The player that owns the cell.

        If the cell is not owned by any player, this property will be 0.
        Otherwise, it will be the number of the player that owns the cell.

        Returns:
            int: The player that owns the cell or 0 if the cell is not owned.
        """
        return self._player_owner

    @player_owner.setter
    def player_owner(self, value: int) -> None:
        """
        Sets the player that owns the cell.

        If the given player is 0, the cell is set to not be owned by any player.
        Otherwise, the cell is set to be owned by the given player.

        Args:
            value (int): The new player that owns the cell.
        """
        self._player_owner = value

    def is_owned(self) -> bool:
        """
        Checks if the cell is owned by any player.

        Returns:
            bool: True if the cell is owned by a player, False otherwise.
        """
        return self._player_owner != 0

    @property
    def can_be_captured(self) -> bool:
        """
        Checks if the cell can be captured by a player.

        Returns:
            bool: True if the cell can be captured, False otherwise.
        """
        return self._can_be_captured

    @can_be_captured.setter
    def can_be_captured(self, value: bool) -> None:
        """
        Sets if the cell can be captured by a player.

        If the given value is False, the cell cannot be captured by any player.
        Otherwise, the cell can be captured by any player.

        Args:
            value (bool): The new value for can_be_captured.
        """
        self._can_be_captured = value

    def __str__(self) -> str:
        if self.can_be_captured:
            return f"{self._current_capacity}/{self.max_capacity}"

        return "X"

class CellCoords(namedtuple("CellCoords", ["x", "y"])):
    def is_nearby(self, coords: CellCoords) -> bool:
        """
        Checks if the given cell coordinates is nearby this cell coordinates.

        A cell is nearby if it is at most one cell away in any direction (up, down,
        left, right, and diagonals).

        Args:
            coords (CellCoords): The cell coordinates to check.

        Returns:
            bool: True if the cell is nearby, False otherwise.
        """
        return abs(self.x - coords.x) <= 1 and abs(self.y - coords.y) <= 1

class Map():
    _cells: list

    def __init__(self, width, height) -> None:
        """
        Initializes the map with the given width and height.

        The map is a 2D list of Cells, where each cell has a maximum capacity of 10.
        The map is not initialized with any player owners.

        Args:
            width (int): The width of the map.
            height (int): The height of the map.
        """
        self._cells = [
            [
                Cell(random.randint(10, 1000), ticks_to_fill=random.randint(0, 5))
                for _ in range(width)
            ]
            for _ in range(height)
        ]

    def get_cell(self, coords: CellCoords) -> Cell:
        """
        Retrieves the cell at the specified coordinates.

        Args:
            coords (CellCoords): The coordinates of the cell to retrieve.

        Returns:
            Cell: The cell located at the specified coordinates.

        Raises:
            ValueError: If the x or y coordinate is out of the map's range.
        """
        if coords.x < 0 or coords.x >= len(self._cells[0]):
            raise ValueError("x is out of range")
        if coords.y < 0 or coords.y >= len(self._cells):
            raise ValueError("y is out of range")

        return self._cells[coords.y][coords.x]

    def is_cell_valid(self, coords: CellCoords) -> bool:
        """
        Checks if the cell coordinates are within the map's bounds.

        Args:
            coords (CellCoords): The coordinates of the cell to check.

        Returns:
            bool: True if the cell is within the map's bounds, False otherwise.
        """
        return 0 <= coords.x < self.width and 0 <= coords.y < self.height

    @property
    def height(self) -> int:
        """
        The height of the map.

        Returns:
            int: The height of the map.
        """
        return len(self._cells)

    @property
    def width(self) -> int:
        """
        The width of the map.

        Returns:
            int: The width of the map.
        """
        return len(self._cells[0])
