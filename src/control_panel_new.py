from PyQt5.QtCore import Qt, QTimer, QTextCodec, QProcess
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QFrame, QPushButton, QPlainTextEdit, QHBoxLayout, QLabel, QSplitter, QListWidget, QGridLayout
from datetime import datetime
import gpustat
import sys

# Set the default font for the application
from PyQt5.QtGui import QFont
QApplication.setFont(QFont("Arial", 16))

class GPUUtilizationMonitor(QWidget):
    def __init__(self):
        super().__init__()

        # Create a QVBoxLayout for the GPU Utilization Monitor widget
        layout = QVBoxLayout(self)

        # Add a title to the GPU Utilization Monitor at the top
        title_label = QLabel('<b>GPU Utilization Monitor</b>', self)
        title_label.setFont(QFont('Arial', 20))  # Set font size to 20
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

class Ros2ListWidget(QListWidget):
    def __init__(self, command, title_label):
        super().__init__()

        # Set up a QProcess to run the specified command
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.read_output)

        self.process.start(command[0], command[1:])

    def read_output(self):
        # Read and decode the standard output of the process
        output = QTextCodec.codecForMib(106).toUnicode(self.process.readAllStandardOutput())
        item_list = output.split('\n')  # Fix the split function

        # Clear existing items before adding new ones
        self.clear()

        self.addItems(item_list)

class SimpleMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window with the title "Pipeline Controller"
        self.setWindowTitle('Pipeline Controller')
        self.setGeometry(100, 100, 2000, 1200)

        # --------------- left half ---------------------------
        # Create a central widget and layout for the main window
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a QHBoxLayout to organize widgets horizontally
        central_layout = QHBoxLayout(central_widget)

        # Create a GPU Utilization Monitor widget for the left half
        gpu_monitor_widget = GPUUtilizationMonitor()

        # Add the QTextBrowser and GPU Utilization Monitor to the left half
        central_layout.addWidget(gpu_monitor_widget, stretch=2)

        # --------------- right half ---------------------------

        # Create a widget for the right half
        right_widget = QWidget(self)

        # Create a QGridLayout for the right side
        right_side_layout = QGridLayout()

        # Add the 'Node List' title label at row 0, column 0
        node_list_title = QLabel('<b>Activate Node List</b>', self)
        node_list_title.setFont(QFont('Arial', 20))  # Set font size to 20
        right_side_layout.addWidget(node_list_title, 0, 0)

        self.node_list_widget = Ros2ListWidget(['ros2', 'node', 'list'], node_list_title)

        # right_side_layout.addWidget(node_list_title, 0, 0)

        # Add the 'Node List' widget at row 1, column 0
        right_side_layout.addWidget(self.node_list_widget, 1, 0)

        # Add the 'Topic List' title label at row 2, column 0
        topic_list_title = QLabel('<b>Topic List</b>', self)
        topic_list_title.setFont(QFont('Arial', 20))  # Set font size to 20
        right_side_layout.addWidget(topic_list_title, 2, 0)

        self.topic_list_widget = Ros2ListWidget(['ros2', 'topic', 'list'], topic_list_title)
        # Add the 'Topic List' widget at row 3, column 0
        right_side_layout.addWidget(self.topic_list_widget, 3, 0)

        # Set the right_side_layout as the layout for the right_widget
        right_widget.setLayout(right_side_layout)

        # ------------------------------------------------
        # Create a QSplitter for organizing widgets
        splitter = QSplitter(Qt.Horizontal)

        # Add the right widget to the right half
        splitter.addWidget(gpu_monitor_widget)
        splitter.addWidget(right_widget)

        # Set the initial sizes of the widgets in the splitter
        splitter.setSizes([int(self.width() * 0.3), int(self.width() * 0.7)])

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
        close_button.move(self.width() - 150, self.height() - 70)
        close_button.show()

        # Add the 'Refresh' button to the bottom right corner
        self.refresh_button = QPushButton('Refresh', self)
        self.refresh_button.clicked.connect(self.refresh_lists)
        self.refresh_button.move(self.width() - 300, self.height() - 70)
        self.refresh_button.show()

    def refresh_lists(self):
        # Refresh the data in the right lists (Node List and Topic List)
        for widget in [self.node_list_widget, self.topic_list_widget]:
            # Terminate the existing process if running
            widget.process.terminate()
            widget.process.waitForFinished()

            # Create a new process to run the respective command
            new_process = QProcess(self)
            new_process.setProcessChannelMode(QProcess.MergedChannels)
            new_process.readyReadStandardOutput.connect(widget.read_output)

            # Construct the command and start the new process
            command = [widget.process.program()] + widget.process.arguments()
            new_process.start(command[0], command[1:])
            
            # Assign the new process to the widget
            widget.process = new_process

            # Clear existing items before adding new ones
            widget.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SimpleMainWindow()
    window.show()
    sys.exit(app.exec_())
