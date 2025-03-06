from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog
from PyQt5.QtCore import QThread, pyqtSignal
from mapping.mapping import run_mapping

# Custom QThread class for running the mapping mission
class MappingThread(QThread):
    # Signal to indicate when the task is finished
    finished = pyqtSignal()
    # Signal to pass the Excel file path to the mapping function
    excel_file_selected = pyqtSignal(str)

    def run(self):
        # Run the mapping mission with the selected Excel file
        run_mapping(self.excel_file_path)
        # Emit the finished signal
        self.finished.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mission Control")
        self.setGeometry(100, 100, 300, 200)

        # Create buttons
        self.mapping_button = QPushButton("Mapping", self)
        self.measurement_button = QPushButton("Measurement", self)
        self.modeling_button = QPushButton("3D Modeling", self)
        self.open_file_button = QPushButton("Open File", self)

        # Connect buttons to functions
        self.mapping_button.clicked.connect(self.start_mapping)
        self.measurement_button.clicked.connect(self.run_measurement)
        self.modeling_button.clicked.connect(self.run_modeling)
        self.open_file_button.clicked.connect(self.open_file_dialog)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.mapping_button)
        layout.addWidget(self.measurement_button)
        layout.addWidget(self.modeling_button)
        layout.addWidget(self.open_file_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Initialize the mapping thread
        self.mapping_thread = MappingThread()
        # Store the selected Excel file path
        self.excel_file_path = None

    def open_file_dialog(self):
        # Open a file dialog to select an Excel file
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Excel File", "", "Excel Files (*.xlsx *.xls)")
        if file_path:
            print(f"Selected file: {file_path}")
            self.excel_file_path = file_path

    def start_mapping(self):
        if not self.excel_file_path:
            print("Error: No Excel file selected.")
            return

        # Disable the mapping button to prevent multiple clicks
        self.mapping_button.setEnabled(False)
        # Pass the selected Excel file path to the thread
        self.mapping_thread.excel_file_path = self.excel_file_path
        # Start the mapping thread
        self.mapping_thread.start()
        # Re-enable the button when the thread finishes
        self.mapping_thread.finished.connect(self.on_mapping_finished)

    def on_mapping_finished(self):
        # Re-enable the mapping button
        self.mapping_button.setEnabled(True)

    def run_measurement(self):
        print("Running Measurement Mission")
        # Add your measurement logic here

    def run_modeling(self):
        print("Running 3D Modeling Mission")
        # Add your 3D modeling logic here