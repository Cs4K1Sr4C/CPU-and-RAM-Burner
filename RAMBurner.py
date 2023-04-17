import os
import sys
import threading
import time
import psutil
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QLabel, QSlider
from PyQt5.QtCore import Qt

try:
    from PyQt5.QtCore import Qt
except ImportError:
    raise ImportError("PyQt5 is required. Install it using 'pip install pyqt5'")

class RAMFlooder(threading.Thread):
    def __init__(self, aggressiveness):
        super().__init__()
        self.aggressiveness = aggressiveness
        self.running = True

    def run(self):
        data = b'\0' * (10485760 * self.aggressiveness)
        while self.running:
            try:
                data = data + data
            except MemoryError:
                data = b'\0' * (10485760 * self.aggressiveness)

    def stop(self):
        self.running = False

class CPUFlooder(threading.Thread):
    def __init__(self, aggressiveness):
        super().__init__()
        self.aggressiveness = aggressiveness
        self.running = True

    def run(self):
        start_time = time.time()
        while self.running:
            if time.time() - start_time > self.aggressiveness:
                time.sleep(self.aggressiveness)
                start_time = time.time()

    def stop(self):
        self.running = False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aggressive CPU and RAM Flooder")
        self.initUI()
        self.cpu_flooder_threads = []
        self.ram_flooder = None

    def initUI(self):
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)

        self.cpu_flood_button = QPushButton("Start CPU Flooding", self)
        self.cpu_flood_button.setCheckable(True)
        self.cpu_flood_button.clicked.connect(self.toggle_cpu_flood)
        layout.addWidget(self.cpu_flood_button)

        self.ram_flood_button = QPushButton("Start RAM Flooding", self)
        self.ram_flood_button.setCheckable(True)
        self.ram_flood_button.clicked.connect(self.toggle_ram_flood)
        layout.addWidget(self.ram_flood_button)

        self.cpu_slider_label = QLabel("CPU Aggressiveness: 1")
        layout.addWidget(self.cpu_slider_label)

        self.cpu_slider = QSlider(Qt.Horizontal, self)
        self.cpu_slider.setMinimum(1)
        self.cpu_slider.setMaximum(10)
        self.cpu_slider.setValue(1)
        self.cpu_slider.valueChanged.connect(self.update_cpu_slider_label)
        layout.addWidget(self.cpu_slider)
        
        self.temperature_label = QLabel("Temperature: ")
        layout.addWidget(self.temperature_label)

        self.ram_slider_label = QLabel("RAM Aggressiveness: 1")
        layout.addWidget(self.ram_slider_label)

        self.ram_slider = QSlider(Qt.Horizontal, self)
        self.ram_slider.setMinimum(1)
        self.ram_slider.setMaximum(10)
        self.ram_slider.setValue(1)
        self.ram_slider.valueChanged.connect(self.update_ram_slider_label)
        layout.addWidget(self.ram_slider)

        self.setCentralWidget(central_widget)

    def update_cpu_slider_label(self, value):
        self.cpu_slider_label.setText(f"CPU Aggressiveness: {value}")

    def update_ram_slider_label(self, value):
        self.ram_slider_label.setText(f"RAM Aggressiveness: {value}")

    def toggle_cpu_flood(self, checked):
        if checked:
            self.cpu_flood_button.setText("Stop CPU Flooding")
            aggressiveness = self.cpu_slider.value() / 10
            for _ in range(os.cpu_count()):
                cpu_flooder = CPUFlooder(aggressiveness)
                self.cpu_flooder_threads.append(cpu_flooder)
                cpu_flooder.start()
        else:
            self.cpu_flood_button.setText("Start CPU Flooding")
            for cpu_flooder in self.cpu_flooder_threads:
                cpu_flooder.stop()
                cpu_flooder.join()
            self.cpu_flooder_threads.clear()
            
    def update_temperature(self):
        temperatures = psutil.sensors_temperatures()
        if 'coretemp' in temperatures:
            avg_temp = sum(sensor.current for sensor in temperatures['coretemp']) / len(temperatures['coretemp'])
            self.temperature_label.setText(f"Temperature: {avg_temp:.1f}°C")
        else:
            self.temperature_label.setText("Temperature: N/A")

    def toggle_ram_flood(self, checked):
        if checked:
            self.ram_flood_button.setText("Stop RAM Flooding")
            aggressiveness = self.ram_slider.value()
            self.ram_flooder = RAMFlooder(aggressiveness)
            self.ram_flooder.start()
        else:
            self.ram_flood_button.setText("Start RAM Flooding")
            self.ram_flooder.stop()
            self.ram_flooder.join()
            self.ram_flooder = None

    def closeEvent(self, event):
        for cpu_flooder in self.cpu_flooder_threads:
            cpu_flooder.stop()
            cpu_flooder.join()

        if self.ram_flooder:
            self.ram_flooder.stop()
            self.ram_flooder.join()

        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

