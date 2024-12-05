"""
1. Подключение
2. Получение лобби
3. Получение карты
4. Переход в статус готовности
5. Начало игры со стороны сервера
6. Процесс игры посредством передачи сигналов о передвижениях/уничтожении игроков
7. Получение от сервера "конца игры"
"""

from typing import Any


class NetworkCommand:
    CONNECT = 0
    """
    Запрос: получить player_id

    Передача: player_id
    """
    PLAYER_CONNECTED = 1
    """ Передача: player_id, color (QColor) """
    GAME_HANDLER = 2
    """ Передача: GameHandler """
    CHANGE_READY = 3
    """ Передача: ready state (bool) """
    READY_STATE_CHANGED = 4
    """ Передача: player_id, ready state (bool) """
    # GameHandler Codes
    CAPTURED = 10
    """ Передача: player_id, CellCoords """
    TROOPS_MOVED = 11
    """
    Передача: player_id, from_cell (CellCoords), to_cell (CellCoords), num_of_troops
    """
    ELIMINATED = 12
    """ Передача player_id """
    GAME_STATE = 13
    """ Передача GameStatus """

class NetworkPacket:
    """
    Если data None, то это запрос.

    Иначе - передача (ожидаемую data см. NetworkCommand)
    """
    def __init__(self, command: NetworkCommand, data: Any | None) -> None:
        self.command = command
        self.data = data
