from PyQt6.QtWidgets import QWidget
from PyQt6.QtNetwork import QTcpSocket
from PyQt6 import uic

class MessengerWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        
        self._socket = QTcpSocket(self)
        
        self.ui = uic.loadUi("client.ui", self)
        self.__connect_signals()
        
    def __connect_signals(self) -> None:
        self.ui._pb_connect.clicked.connect(self.on_pb_connect_clicked)
        
        self.ui._pb_send_msg.clicked.connect(self.on_send_msg_clicked)
        
        self._socket.connected.connect(self.on_connected)
        self._socket.disconnected.connect(self.on_disconnected)
        self._socket.readyRead.connect(self.on_data_received)

    def on_pb_connect_clicked(self) -> None:
        if self._socket.state() == QTcpSocket.SocketState.ConnectedState:
            self.ui._pb_connect.setEnabled(False)
            self._socket.disconnectFromHost()
            self.ui._w_messanges.setEnabled(False)
            self.ui._te_got_msg.setText("")
            return

        target = self.ui._le_target_addr.text().strip()
        if not target:
            return

        print("Connecting to", target)
        ip, port = self.ui._le_target_addr.text().split(":")
        self._socket.connectToHost(ip, int(port))
        self.ui._pb_connect.setEnabled(False)

    def on_connected(self) -> None:
        print("Connected to server!")
        self.ui._pb_connect.setEnabled(True)
        self.ui._pb_connect.setText("Disconnect")
        self.ui._w_messanges.setEnabled(True)
        self.ui._te_got_msg.setText("Connected to server!")

    def on_disconnected(self) -> None:
        print("Disconnected from server!")
        self.ui._te_got_msg.append("Disconnected from server!")
        self.ui._w_messanges.setEnabled(False)
        self.ui._pb_connect.setText("Connect")
        self.ui._pb_connect.setEnabled(True)

    def on_data_received(self) -> None:
        data = self._socket.readAll().data().decode()
        self.ui._te_got_msg.append(data)

    def on_send_msg_clicked(self) -> None:
        msg = self.ui._le_msg_to_send.text()
        self.send_message(msg)

    def send_message(self, message: str) -> None:
        if self._socket.state() == QTcpSocket.SocketState.ConnectedState:
            self._socket.write(message.encode())
            print("Sent:", message)
            self.ui._te_got_msg.append(f"Sent: {message}")
        else:
            print("Not connected to server.")
            self.ui._te_got_msg.append("Not connected to server.")
