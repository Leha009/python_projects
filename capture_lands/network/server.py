import sys

from PyQt6.QtWidgets import QMainWindow, QWidget, QApplication
from PyQt6.QtNetwork import QTcpServer, QTcpSocket, QHostAddress
from PyQt6.QtGui import QColor
from PyQt6 import uic

from .network_protocol import NetworkPacket, NetworkCommand
from ..handler import GameHandler
from ..map import Map

class ServerWindow(QMainWindow):
    def __init__(
        self,
        game_handler: GameHandler,
        address: str = "127.0.0.1",
        port: int = 1250,
        parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)

        self._game_hander = game_handler

        self._server = QTcpServer(self)
        self._addr = QHostAddress(address)
        self._port = port
        self._server.listen(self._addr, self._port)
        self._server.newConnection.connect(self.on_new_connection)

        self._clients: set[QTcpSocket] = set()
        self._clients_names: dict[QTcpSocket, str] = dict()
        self._clients_colors: dict[QTcpSocket, QColor] = dict()

        self.ui = uic.loadUi("server.ui", self)

        server_addr = f"{self._addr.toString()}:{self._port}"
        self.log_action(f"Server started on {server_addr}")

        map = self._game_hander.get_map()
        map_size = f"{map.width}x{map.height}"
        self.log_action(f"Map size is {map_size}")

        self.log_action(f"Players count {self._game_hander.alive_players_count()}")

    def log_action(self, text: str) -> None:
        self.ui._te_logs.append(text)

    def on_new_connection(self) -> None:
        connection = self._server.nextPendingConnection()
        self._clients.add(connection)
        connection.readyRead.connect(self.on_data_received)
        connection.disconnected.connect(self.on_disconnected)

        client_addr = f"{connection.peerAddress().toString()}:{connection.peerPort()}"
        self.log_action(f"New connection from {client_addr}")

    def on_disconnected(self) -> None:
        connection: QTcpSocket = self.sender()
        self._clients.remove(connection)

        client_addr = f"{connection.peerAddress().toString()}:{connection.peerPort()}"
        self.log_action(f"Disconnected from {client_addr}")

    def on_data_received(self) -> None:
        conn: QTcpSocket = self.sender()
        data = conn.readAll().data().decode()
        if conn not in self._clients_names:
            self._clients_names[conn] = data

            client_addr = f"{conn.peerAddress().toString()}:{conn.peerPort()}"
            client_name = self._clients_names[conn]
            self.log_action(f"New client: {client_addr} ({client_name})")
            return

        client_addr = f"{conn.peerAddress().toString()}:{conn.peerPort()}"
        client_name = self._clients_names[conn]
        self.log_action(f"Received from {client_addr} ({client_name}): {data}")
        for client in self._clients:
            if client != conn:
                client.write(": ".join([self._clients_names[conn], data]).encode())

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(
            "Usage: server.py [address:port] [map_size] [num_of_players] [num_of_bots]")
        print('Example: python server.py "127.0.0.1:1250" 7x7 4 4')
        sys.exit(1)

    ip, port = sys.argv[1].split(":")
    port = int(port)

    map_width, map_height = map(int, sys.argv[2].split("x"))
    map = Map(map_width, map_height)

    num_of_players = int(sys.argv[3])
    num_of_bots = int(sys.argv[4])

    game_handler = GameHandler(map, num_of_players, num_of_bots)
    app = QApplication([])
    window = ServerWindow(game_handler, ip, port)
    window.show()
    sys.exit(app.exec())
