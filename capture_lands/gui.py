import random
import time
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QGridLayout,
    QHBoxLayout,
    QSpacerItem,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLabel
)
from PyQt6.QtCore import Qt, QEvent
from PyQt6 import uic
from PyQt6.QtGui import QColor

from handler import GameHandler
from map import CellCoords, Map

TIME_CLICK_TIMEOUT = 2
PLAYER_ID = 1

class MapGUI(QMainWindow):
    game_handler: GameHandler

    _source_clicked: CellCoords
    _target_clicked: CellCoords
    _time_on_click: int

    def __init__(self, players: int = 2) -> None:
        """
        Initialize the user interface from a .ui file.
        """
        super().__init__()
        uic.loadUi('gui.ui', self)

        # Аннотации ко всем элементам, созданным и указанным в gui.ui
        self.centralwidget: QWidget  # Центральный виджет
        self.gridLayoutWidget: QWidget  # Виджет для сетки
        self.gridLayout: QGridLayout  # Основная сетка
        self.horizontalLayout: QHBoxLayout  # Горизонтальная сетка
        self.horizontalSpacer: QSpacerItem  # Горизонтальный спейсер
        self.l_ticks: QLabel  # Метка для отображения количества тиков
        self.player_color: QPushButton  # Метка для отображения цвета игрока
        self.map: QTableWidget  # Таблица для отображения карты
        self.pause_button: QPushButton  # Кнопка для паузы

        self.centralWidget().setLayout(self.gridLayout)

        self.game_handler = GameHandler(Map(10, 10), players)
        self.connect_signals()
        self.init_colors(players=players)
        self.init_map()
        self.update()

        self._source_clicked = None
        self._target_clicked = None
        self._time_on_click = 0

    def connect_signals(self) -> None:
        self.pause_button.clicked.connect(self.start_stop)
        self.game_handler.tick.connect(self.update)

        self.map.viewport().installEventFilter(self)

    def init_colors(self, players: int) -> None:
        self._players_colors = list()
        for _ in range(players):
            self._players_colors.append(QColor(
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
                255
            ))

        self.player_color.setStyleSheet(
            f"background-color: {self._players_colors[PLAYER_ID - 1].name()};")

    def init_map(self) -> None:
        self.map.setRowCount(self.game_handler.get_map().height)
        self.map.setColumnCount(self.game_handler.get_map().width)
        for y in range(self.game_handler.get_map().height):
            for x in range(self.game_handler.get_map().width):
                cell = self.game_handler.get_map().get_cell(CellCoords(x, y))
                item = QTableWidgetItem(str(cell))
                self.map.setItem(y, x, item)

    def update(self) -> None:
        ticks = self.game_handler.get_ticks()
        self.l_ticks.setText(f"ticks: {ticks}")

        for y in range(self.game_handler.get_map().height):
            for x in range(self.game_handler.get_map().width):
                cell = self.game_handler.get_map().get_cell(CellCoords(x, y))
                self.map.item(y, x).setText(str(cell))
                if cell.player_owner:
                    alpha = max(cell.current_capacity * 255 // cell.max_capacity, 70)
                    alpha = min(alpha, 255)
                    color: QColor = self._players_colors[cell.player_owner - 1]
                    color.setAlpha(alpha)
                    self.map.item(y, x).setBackground(color)

    def eventFilter(self, source, event: QEvent) -> bool:
        if event.type() == QEvent.Type.MouseButtonPress:
            now = time.time()
            if now - self._time_on_click > TIME_CLICK_TIMEOUT:
                self._source_clicked = None
                self._target_clicked = None

            self._time_on_click = now

            if event.button() == Qt.MouseButton.LeftButton:
                index = self.map.indexAt(event.pos())
                if index.isValid():
                    self._source_clicked = CellCoords(index.column(), index.row())
                    if self._target_clicked is not None:
                        self.game_handler.move_troops(
                            PLAYER_ID, self._target_clicked, self._source_clicked)
                        self._source_clicked = None
                        self._target_clicked = None

            elif event.button() == Qt.MouseButton.RightButton:
                index = self.map.indexAt(event.pos())
                if index.isValid():
                    self._target_clicked = CellCoords(index.column(), index.row())
                    if self._source_clicked is not None:
                        self.game_handler.move_troops(
                            PLAYER_ID, self._target_clicked, self._source_clicked)
                        self._source_clicked = None
                        self._target_clicked = None

        return super().eventFilter(source, event)

    # signals
    def start_stop(self) -> None:
        if self.game_handler.is_stopped():
            self.game_handler.resume()
            self.pause_button.setText("Pause")
        else:
            self.game_handler.stop()
            self.pause_button.setText("Resume")

def main() -> None:
    """
    Main function to start the application.
    """
    app = QApplication([])
    map_gui = MapGUI()
    map_gui.show()
    app.exec()

if __name__ == "__main__":
    main()
