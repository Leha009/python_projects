from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtNetwork import QTcpSocket

from ..handler import GameHandler
from .network_protocol import NetworkPacket, NetworkCommand

class CaptureClient(QObject):
    player_connected = pyqtSignal(int, object)

    _socket: QTcpSocket

    _game_handler: GameHandler
    _player_id: int

    def get_game_handler(self) -> GameHandler:
        return self._game_handler

    def get_player_id(self) -> int:
        return self._player_id
