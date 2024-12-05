from PyQt6.QtWidgets import QWidget

from PyQt6.QtNetwork import QTcpServer, QTcpSocket, QHostAddress

from PyQt6 import uic

class ServerWidget(QWidget):
    def __init__(
        self,
        address: str = "127.0.0.1",
        port: int = 1250,
        parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._server = QTcpServer(self)
        self._addr = QHostAddress(address)
        self._port = port
        self._server.listen(self._addr, self._port)
        self._server.newConnection.connect(self.on_new_connection)

        self._clients: set[QTcpSocket] = set()
        self._clients_names: dict[QTcpSocket, str] = dict()

        self.ui = uic.loadUi("server.ui", self)
        self.log_action(f"Server started on {self._addr.toString()}:{self._port}\n")

    def log_action(self, text: str) -> None:
        self.ui._te_logs.append(text)

    def on_new_connection(self) -> None:
        connection = self._server.nextPendingConnection()
        self._clients.add(connection)
        connection.readyRead.connect(self.on_data_received)
        connection.disconnected.connect(self.on_disconnected)
        self.log_action(f"New connection from {connection.peerAddress().toString()}:{connection.peerPort()}\n")

    def on_disconnected(self) -> None:
        connection: QTcpSocket = self.sender()
        self._clients.remove(connection)
        self.log_action(f"Disconnected from {connection.peerAddress().toString()}:{connection.peerPort()}\n")

    def on_data_received(self) -> None:
        connection: QTcpSocket = self.sender()
        data = connection.readAll().data().decode()
        if connection not in self._clients_names:
            self._clients_names[connection] = data
            self.log_action(f"New client: {connection.peerAddress().toString()}:{connection.peerPort()} ({self._clients_names[connection]})\n")
            return

        self.log_action(f"Received from {connection.peerAddress().toString()}:{connection.peerPort()} ({self._clients_names[connection]}): {data}\n")
        for client in self._clients:
            if client != connection:
                client.write(": ".join([self._clients_names[connection], data]).encode())
