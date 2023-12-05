from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QFrame, QPushButton, QPlainTextEdit, QHBoxLayout, QLabel, QSplitter
from datetime import datetime
import gpustat
import sys

# Set the default font for the application
from PyQt5.QtGui import QFont
QApplication.setFont(QFont("Arial", 14))

class GPUUtilizationMonitor(QWidget):
    def __init__(self):
        super().__init__()

        # Create a QVBoxLayout for the GPU Utilization Monitor widget
        layout = QVBoxLayout(self)

        # Add a title to the GPU Utilization Monitor at the top
        title_label = QLabel('GPU Utilization Monitor', self)
        title_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        layout.addWidget(title_label)

        # Create a QTextBrowser to display GPU information
        self.text_browser = QPlainTextEdit(self)
        self.text_browser.setReadOnly(True)
        layout.addWidget(self.text_browser, stretch=1)

        # List to store GPU information records
        self.gpu_info_stack = []

        # Set up a timer to update GPU information
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_gpu_information)
        self.timer.start(1000)  # Update every 1000 milliseconds (1 second)

    def update_gpu_information(self):
        try:
            # Use gpustat to get GPU information
            gpu_stats = gpustat.new_query()

            # Collect GPU utilization information
            gpu_info = [f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - "
                        f"GPU {gpu.index}: {gpu.entry['memory.used']}/{gpu.entry['memory.total']} MB "
                        f"({gpu.entry['utilization.gpu']}%)"
                        for gpu in gpu_stats.gpus]

            # Store the current GPU information record
            self.gpu_info_stack.append('\n'.join(gpu_info))

            # Keep only the most recent 20 records in the stack
            self.gpu_info_stack = self.gpu_info_stack[-20:]

            # Display GPU information in the QTextBrowser
            output = '\n\n'.join(reversed(self.gpu_info_stack))  # Display the most recent records first
            self.text_browser.setPlainText(output)
        except Exception as e:
            print(f"Error retrieving GPU information: {e}")


class SimpleMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window with the title "Pipeline Controller"
        self.setWindowTitle('Pipeline Controller')
        self.setGeometry(100, 100, 2000, 1200)

        # Create a central widget and layout for the main window
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a QHBoxLayout to organize widgets horizontally
        central_layout = QHBoxLayout(central_widget)

        # # Add a separator line (QFrame) between left and right halves
        # separator_line = QFrame(self)
        # separator_line.setFrameShape(QFrame.VLine)
        # separator_line.setFrameShadow(QFrame.Sunken)
        # separator_line.setStyleSheet("color: gray; border: 1px solid gray;")

        # Create a GPU Utilization Monitor widget for the left half
        gpu_monitor_widget = GPUUtilizationMonitor()

        # Add the QTextBrowser and GPU Utilization Monitor to the left half
        central_layout.addWidget(gpu_monitor_widget, stretch=2)

        # # Add the separator line between left and right halves
        # central_layout.addWidget(separator_line)

        # Create a widget for the right half
        right_widget = QWidget(self)
        right_layout = QVBoxLayout(right_widget)

        # Add a label to the right half
        right_label = QLabel('Right', self)
        right_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        right_layout.addWidget(right_label)

        # Add the right widget to the right half
        central_layout.addWidget(right_widget, stretch=1)

        # Create a QSplitter for organizing widgets
        splitter = QSplitter(Qt.Horizontal)

        # Add the right widget to the right half
        splitter.addWidget(gpu_monitor_widget)
        splitter.addWidget(right_widget)

        # Set the initial sizes of the widgets in the splitter
        splitter.setSizes([int(self.width() * 0.7), int(self.width() * 0.3)])

        # Set the style for the splitter
        splitter.setStyleSheet("QSplitter::handle { background-color: gray; border: 1px solid gray; }")

        # Set the splitter as the central widget
        self.setCentralWidget(splitter)

        # Add a close button to the bottom-right corner
        close_button = QPushButton('Close', self)
        close_button.clicked.connect(self.close)
        close_button.setStyleSheet("QPushButton { background-color: red; color: white; }")
        close_button.setMaximumWidth(100)
        close_button.setMaximumHeight(30)

        # Add the close button to the central layout
        central_layout.addWidget(close_button, alignment=Qt.AlignBottom | Qt.AlignRight)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SimpleMainWindow()
    window.show()
    sys.exit(app.exec_())
