import sys

from PyQt6.QtCore import QTimer, QTime, QUrl, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QTimeEdit, QWidget, QCheckBox, QLabel, QSlider, QMenu, QSystemTrayIcon
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtGui import QPixmap, QAction, QIcon
from PyQt6.QtNetwork import QLocalServer, QLocalSocket

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Container
        pageLayout = QVBoxLayout()
        container = QWidget()
        container.setLayout(pageLayout)
        self.setCentralWidget(container)
        self.setWindowTitle("Break Timer")

        # Button
        self.CreateButton()
        
        # Timer

        self.timer = QTimer()
        self.timer.timeout.connect(self.UpdateTimer)
        self.timerActive = False

        # Timer widget

        self.timeEdit = QTimeEdit()
        self.timeEdit.setDisplayFormat("HH:mm:ss")
        self.remainingSeconds = 0
        self.tempSeconds = 0
        self.timeEdit.setFixedSize(470, 150)

        # AutoRestart CheckBox widget

        self.restartCheckBox = QCheckBox("Auto restart timer?")

        # Picture CheckBox widget

        self.popucCheckBox = QCheckBox("Use popup image? (Warning! It can minimize a fullscreen window)")

        # Slider widget

        self.volumeSlider = QSlider(Qt.Orientation.Horizontal, self)
        self.volumeSlider.setMinimum(0)
        self.volumeSlider.setMaximum(100)
        self.volumeSlider.setValue(100)
        self.volumeSlider.valueChanged.connect(self.DisplayVolume)

        self.volumeLabel = QLabel("Volume: 100")


        # Popup image

        self.label = QLabel(self)
        self.pixmap = QPixmap("Images/Popup/image.png")

        self.label.setPixmap(self.pixmap)
        self.label.setScaledContents(True)

        # Sound

        self.sound = QSoundEffect()
        self.sound.setSource(QUrl.fromLocalFile("Sounds/sound.wav"))
        
        pageLayout.addWidget(self.timeEdit)
        pageLayout.addWidget(self.restartCheckBox)
        pageLayout.addWidget(self.popucCheckBox)
        pageLayout.addWidget(self.label)
        pageLayout.addWidget(self.volumeSlider)
        pageLayout.addWidget(self.volumeLabel)
        pageLayout.addWidget(self.button)

        # Server

        self.server = QLocalServer(self)
        self.server.listen("BreakTimer")
        self.server.newConnection.connect(self.restore_window)

        # Tray

        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(QIcon("Images/Icon/icon.png"))

        menu = QMenu()

        showAction = QAction("Open", self)
        showAction.triggered.connect(self.show)

        exitAction = QAction("Exit", self)
        exitAction.triggered.connect(QApplication.quit)

        menu.addAction(showAction)
        menu.addAction(exitAction)

        self.tray.setContextMenu(menu)
        self.tray.show()


        self.setFixedSize(500, 700)
        self.setWindowIcon(QIcon("Images/Icon/icon.png"))
    
    def CreateButton(self):
        self.button = QPushButton("Start Timer")
        self.button.setCheckable(True)
        self.button.clicked.connect(self.SwitchTimer)
        self.button.setMinimumSize(450, 200) 

    def SwitchTimer(self):
        if self.timerActive == True:
            self.StopTimer(True)
        else:
            self.StartTimer()


    def StartTimer(self):
        time = self.timeEdit.time()

        self.remainingSeconds = (
            time.hour() * 3600 +
            time.minute() * 60 +
            time.second()
        )

        self.tempSeconds = self.remainingSeconds

        if self.remainingSeconds <= 0:
            self.StopTimer(False)
            return


        self.timer.start(1000)
        self.button.setChecked(True)
        self.timerActive = True

    def StopTimer(self, manually : bool):
        self.timer.stop()
        self.button.setChecked(False)
        self.timerActive = False
        
        self.remainingSeconds = self.tempSeconds

        hours = self.tempSeconds // 3600
        minutes = (self.tempSeconds % 3600) // 60
        seconds = self.tempSeconds % 60

        self.timeEdit.setTime(
            QTime(hours, minutes, seconds)
        )

        if manually == True:
            return

        self.sound.play()

        if self.popucCheckBox.isChecked():
            self.imageWindow = ImageWindow()

        if self.restartCheckBox.isChecked():
            self.StartTimer()
        
    
    def UpdateTimer(self):
        self.remainingSeconds -= 1

        hours = self.remainingSeconds // 3600
        minutes = (self.remainingSeconds % 3600) // 60
        seconds = self.remainingSeconds % 60

        self.timeEdit.setTime(
            QTime(hours, minutes, seconds)
        )

        if self.remainingSeconds <= 0:
            self.StopTimer(False)
    
    def DisplayVolume(self):
        self.volumeLabel.setText("Volume: " + str(self.sender().value()))
        self.volumeLabel.adjustSize()
        self.sound.setVolume(self.sender().value() / 100)
    
    def closeEvent(self, event):
        event.ignore()
        self.hide()
    
    def restore_window(self):
        client = self.server.nextPendingConnection()

        self.show()
        self.raise_()
        self.activateWindow()

        client.disconnectFromServer()
    


    

class ImageWindow(QLabel):
    def __init__(self):
        super().__init__()

        self.setPixmap(QPixmap("Images/Popup/image.png"))
        self.setScaledContents(True)

        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint
        )

        self.showFullScreen()

    def mousePressEvent(self, event):
        self.close()

socket = QLocalSocket()
socket.connectToServer("BreakTimer")

if socket.waitForConnected(100):
    socket.write(b"show")
    socket.flush()
    sys.exit()

app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)

window = MainWindow()
window.show()

app.exec()