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

from handler import GameStatus
from map import CellCoords, Map

from network.client import CaptureClient

TIME_CLICK_TIMEOUT = 2
PLAYER_ID = 1

class MapGUI(QMainWindow):
    client: CaptureClient
    _players_colors: dict[int, QColor]

    _source_clicked: CellCoords
    _target_clicked: CellCoords
    _time_on_click: int

    def __init__(self, client: CaptureClient, colors: dict[int, QColor]) -> None:
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
        self.l_alive_players: QLabel # Метка для отображения количества живых игроков
        self.player_color: QPushButton  # Метка для отображения цвета игрока
        self.map: QTableWidget  # Таблица для отображения карты
        self.pause_button: QPushButton  # Кнопка для паузы

        self.centralWidget().setLayout(self.gridLayout)

        self.client = client
        self.game_handler = client.get_game_handler()
        self._players_colors = colors
        player_color = self._players_colors[self.client.get_player_id()]
        self.set_player_color(player_color)

        self.connect_signals()
        self.init_map()
        self.update()
        self.on_eliminated(0)

        self._source_clicked = None
        self._target_clicked = None
        self._time_on_click = 0

    def connect_signals(self) -> None:
        self.pause_button.clicked.connect(self.start_stop)

        """ self.game_handler.tick.connect(self.update)
        self.game_handler.game_state_changed.connect(self.on_game_state_changed)
        self.game_handler.eliminated.connect(self.on_eliminated) """

        self.map.viewport().installEventFilter(self)

    def set_player_color(self, color: QColor) -> None:
        self.player_color.setStyleSheet(f"background-color: {color.name()};")

    def init_map(self) -> None:
        """
        Initializes the map table by setting the row and column counts to the height
        and width of the game map, respectively. Then, for each cell in the map, a
        QTableWidgetItem is created with the string representation of the cell and
        set as the item at the corresponding row and column in the table.
        """
        map: Map = self.game_handler.get_map()
        self.map.setRowCount(map.height)
        self.map.setColumnCount(map.width)
        for y in range(map.height):
            for x in range(map.width):
                cell = map.get_cell(CellCoords(x, y))
                item = QTableWidgetItem(str(cell))
                self.map.setItem(y, x, item)

    def update(self) -> None:
        """
        Update the GUI to reflect the current state of the game.

        This method retrieves the current number of ticks from the game handler and updates
        the tick label. It iterates through each cell in the game map, updating the text
        and background color of each cell in the map table according to the cell's attributes.
        If a cell has a player owner, its background color is set based on the player's color
        and the cell's capacity, with the alpha channel adjusted for visibility.
        """
        ticks = self.game_handler.get_ticks()
        self.l_ticks.setText(f"ticks: {ticks}")

        map: Map = self.game_handler.get_map()

        for y in range(map.height):
            for x in range(map.width):
                cell = self.game_handler.get_map().get_cell(CellCoords(x, y))
                self.map.item(y, x).setText(str(cell))
                if cell.player_owner:
                    alpha = max(cell.current_capacity * 255 // cell.max_capacity, 70)
                    alpha = min(alpha, 255)
                    color: QColor = self._players_colors[cell.player_owner - 1]
                    color.setAlpha(alpha)
                    self.map.item(y, x).setBackground(color)

    def eventFilter(self, source, event: QEvent) -> bool:
        """
        Filters and handles mouse button press events on the map widget.

        This method captures mouse button press events to determine source and target
        cells for moving troops in the game. When the left mouse button is pressed, it
        sets the source cell. If a target cell is already selected, it triggers the
        move_troops action between the target and source. When the right mouse button
        is pressed, it sets the target cell and performs the move if a source is
        already selected. The method also enforces a timeout to reset source and target
        selections if the clicks are too far apart in time.

        Args:
            source: The object that generated the event.
            event (QEvent): The event being filtered.

        Returns:
            bool: True if the event should be filtered out, otherwise passes the
            event to the base class implementation.
        """
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
        """
        Toggles the game state between paused and running.

        This method is connected to the pause button's clicked signal. When the
        button is clicked, it checks the current state of the game handler and
        either resumes or stops the game. The button's text is also updated to
        reflect the current state.
        """
        if self.game_handler.is_stopped():
            self.game_handler.resume()
        else:
            self.game_handler.pause()

    def on_game_state_changed(self, state: GameStatus) -> None:
        """
        Updates the pause button text and state based on the game state.

        When the game state changes, this method is called by the game handler
        to update the pause button. The button's text is changed to reflect the
        current state, and the button is disabled if the game is over.
        """
        if state == GameStatus.END:
            self.pause_button.setText("Game END")
            self.pause_button.setEnabled(False)
        elif state == GameStatus.ACTIVE:
            self.pause_button.setText("Pause")
        elif state == GameStatus.PAUSED:
            self.pause_button.setText("Resume")

    def on_eliminated(self, player_id: int) -> None:
        """
        Updates the label displaying the number of alive players when a player is eliminated.

        This method is triggered by the `eliminated` signal from the game handler,
        indicating that a player has been eliminated from the game. It updates the
        label `l_alive_players` to reflect the new count of players still alive.

        Args:
            player_id (int): The ID of the player that has been eliminated.
        """
        self.l_alive_players.setText(
            f"Живых игроков: {self.game_handler.alive_players_count()}")

def main() -> None:
    """
    Main function to start the application.
    """
    app = QApplication([])
    map_gui = MapGUI(
        map_width=7,
        map_height=7,
        num_of_players=4,
        num_of_bots=4
    )
    map_gui.show()
    app.exec()

if __name__ == "__main__":
    main()
