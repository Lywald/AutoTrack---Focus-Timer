import pygetwindow as gw
import psutil



import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QImage
from PIL import Image

import win32process
import win32con
import win32gui
import win32ui

#from PyQt5.QtGui 

class SimpleMainWindow(QMainWindow):
    window_title_to_time = {}  # Dictionary to store window titles and time spent

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Auto Track")
        self.setGeometry(100, 100, 180, 150)  # Set the position and size of the window

        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)


        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        widget.setStyleSheet("background-color: #f3f3f1;") 
        self.setStyleSheet("background-color: #f3f3f1")
        self.windowLabel = QLabel("TEST")
        self.windowLabel.setStyleSheet("background-color: #f3f3f1; text-align: center; height: 30px")
        self.windowLabel.setAlignment(Qt.AlignCenter)
        self.windowLabel.setWordWrap(True)
        self.windowTimerLabel = QLabel("0")
        self.windowTimerLabel.setStyleSheet("background-color: #e8e8e8; font-size: 42pt; height: 30px;")
        self.windowTimerLabel.setAlignment(Qt.AlignCenter)

        self.windowIconImage = self.get_active_window_icon()
        self.windowPixmapLabel = QLabel()
        self.windowPixmapLabel.setStyleSheet("background-color: #f3f3f1; height: 30px; width: 30px")
        self.windowPixmapLabel.setFixedSize(30, 30)  # Set the label's size to 100x30 pixels

        self.windowPixmapLabel.setAlignment(Qt.AlignCenter)
        self.windowPixmapLabel.setPixmap(self.windowIconImage)

        layoutWindowDetails = QHBoxLayout()
        layoutWindowDetails.addWidget(self.windowPixmapLabel)
        layoutWindowDetails.addWidget(self.windowLabel)

        layout.addLayout(layoutWindowDetails)

        layout.addWidget(self.windowTimerLabel)



        # Set the central widget
        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timerEvent)  # Connect the timer to a function
        self.timer.start(1000) 

    def get_active_window_icon(self):
        hwnd = win32gui.GetForegroundWindow()  # Get handle to the active window
        hicon = win32gui.SendMessage(hwnd, win32con.WM_GETICON, win32con.ICON_BIG, 0) or win32gui.GetClassLong(hwnd, win32con.GCL_HICON)
        if not hicon:
            return None

        # Create a device context and bitmap for drawing the icon
        hdcScreen = win32gui.GetDC(hwnd)
        hdcMem = win32ui.CreateDCFromHandle(win32gui.CreateCompatibleDC(hdcScreen))
        bmp = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(win32ui.CreateDCFromHandle(hdcScreen), 32, 32)
        hdcMem.SelectObject(bmp)

        # Draw the icon into the bitmap
        win32gui.DrawIconEx(hdcMem.GetSafeHdc(), 0, 0, hicon, 32, 32, 0, None, win32con.DI_NORMAL)

        # Save the bitmap to a file
        bmpinfo = bmp.GetInfo()
        bmpstr = bmp.GetBitmapBits(True)
        im = Image.frombuffer(
            'RGBA',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRA', 0, 1
        )

        # Clean up
        win32gui.ReleaseDC(hwnd, hdcScreen)
        hdcMem.DeleteDC()
        win32gui.DeleteObject(bmp.GetHandle())

        # Convert PIL image to QPixmap
        im.save('temp_icon.png')
        pixmap = QPixmap('temp_icon.png')
        return pixmap

    def get_active_window_process_name(self):
        active_window_id = None
        try:
            active_window_id = win32gui.GetForegroundWindow()
            for process in psutil.process_iter(['pid', 'name']):
                try:
                    if process.pid == win32process.GetWindowThreadProcessId(active_window_id)[1]:
                        return process.info['name']
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        except Exception as e:
            print(f"Error: {e}")
        return None

    def timerEvent(self):
        # This function will be called every 1 second
        print("Timer event - Perform actions here")
        # Get the currently active window
        active_window = gw.getActiveWindow()
        if active_window is not None:
            print("Current Window Title:", active_window.title)
            self.windowLabel.setText(active_window.title)
            if ("Visual Studio" in active_window.title):
                print("In VS")
            #print("Current Window Class:", active_window.class_name)
            pname = self.get_active_window_process_name()
            if pname not in self.window_title_to_time:
                self.window_title_to_time[pname] = 1
            else:
                self.window_title_to_time[pname] += 1
            self.windowTimerLabel.setText(str(self.window_title_to_time[pname]))
            myic = self.get_active_window_icon()
            if myic is not None:
                self.windowPixmapLabel.setPixmap(myic)
            print("dico: " + str(self.window_title_to_time))
        else:
            print("No active window found.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SimpleMainWindow()
    window.show()
    sys.exit(app.exec_())
