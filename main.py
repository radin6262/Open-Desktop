import sys
import subprocess
import math
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QPixmap, QPainter, QColor, QPen

class WindowsSpinner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(100, 100)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(15) # Smooth 60fps

    def update_animation(self):
        self.angle = (self.angle + 6) % 360
        self.update() # Triggers paintEvent

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        # Draw 6 dots with different offsets to create the "trailing" effect
        for i in range(6):
            # This math creates the classic Windows "variable speed" look
            dot_angle = (self.angle - (i * 15)) * (math.pi / 180)
            x = 50 + 30 * math.cos(dot_angle)
            y = 50 + 30 * math.sin(dot_angle)
            
            # Fade the trailing dots
            opacity = 255 - (i * 40)
            painter.setBrush(QColor(255, 255, 255, max(0, opacity)))
            painter.drawEllipse(x - 3, y - 3, 6, 6)

class StartupScreen(QWidget):
    def __init__(self):
        super().__init__()
        
        # 1. Window Setup
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setStyleSheet("background-color: black;")
        self.showFullScreen()

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(50)

        # 2. Logo
        self.logo_label = QLabel()
        logo_pix = QPixmap("assets/startup.png")
        if not logo_pix.isNull():
            self.logo_label.setPixmap(logo_pix.scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.logo_label.setText("LOGO.PNG MISSING")
            self.logo_label.setStyleSheet("color: white; font-size: 20px;")
        layout.addWidget(self.logo_label, alignment=Qt.AlignCenter)

        # 3. The Custom Drawn Spinner
        self.spinner = WindowsSpinner()
        layout.addWidget(self.spinner, alignment=Qt.AlignCenter)

        # 4. Timing Logic
        # Launch explorer app after 8 seconds
        QTimer.singleShot(8000, self.launch_explorer)

    def launch_explorer(self):
        print("Launching desktop.py...")
        subprocess.Popen([sys.executable, "desktop.py"])
        
        # Wait final 2.5s then kill this process
        QTimer.singleShot(2500, self.kill_self)

    def kill_self(self):
        self.close()
        sys.exit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = StartupScreen()
    sys.exit(app.exec())