import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileDialog, QAction,
                             QHBoxLayout, QVBoxLayout, QWidget, QDoubleSpinBox,
                             QPushButton, QLabel)
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg,
                                                NavigationToolbar2QT)

import matplotlib.pyplot as plt
from superqt import QRangeSlider

# Import the IRG reader functions
from extract_irg import extract_data_from_binary


class ThermalImageApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.figure, self.axis = plt.subplots(figsize=(6, 6))
        self.canvas = None
        self.range_slider = None
        self.colorbar = None
        self.thermal_data = None
        self.thermal_data_fahrenheit = None
        self.slider_min_value = 0
        self.slider_max_value = 100
        self.temp_label = self.figure.text(0.5, 0.01, '', ha='center',
                                           va='bottom', color='black',
                                           fontsize=10)
        self.image_loaded = False
        self.init_ui()

    def init_ui(self):
        """Initialize the UI components."""
        self.setWindowTitle('HeatSeeker')
        self.setup_menu()
        self.setup_layout()
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        self.addToolBar(self.toolbar)

        self.show()

    def setup_menu(self):
        """Setup the menu bar."""
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        open_file = QAction('Open', self)
        open_file.triggered.connect(self.show_dialog)
        file_menu.addAction(open_file)

    def setup_layout(self):
        """Setup the layout of the main window."""
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.mpl_connect('motion_notify_event', self.on_hover)
        self.range_slider = QRangeSlider(self)
        self.range_slider.setRange(0, 100)
        self.range_slider.setValue((0, 100))
        self.range_slider.valueChanged.connect(self.update_image)
        layout = QHBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.range_slider)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Add widgets to set custom min/max values for the slider
        self.min_spinbox = QDoubleSpinBox(self)
        self.min_spinbox.setRange(-100, 100)
        self.min_spinbox.setValue(self.slider_min_value)
        self.max_spinbox = QDoubleSpinBox(self)
        self.max_spinbox.setRange(-100, 100)
        self.max_spinbox.setValue(self.slider_max_value)

        set_range_button = QPushButton("Set Range", self)
        set_range_button.clicked.connect(self.update_slider_range)

        slider_layout = QVBoxLayout()
        slider_layout.addWidget(QLabel("Min Value:"))
        slider_layout.addWidget(self.min_spinbox)
        slider_layout.addWidget(QLabel("Max Value:"))
        slider_layout.addWidget(self.max_spinbox)
        slider_layout.addWidget(set_range_button)
        slider_layout.addWidget(self.range_slider)

        layout.addWidget(self.canvas)
        layout.addLayout(slider_layout)

    def on_hover(self, event):
        """Show the Temp value on the plot"""
        # Check if the mouse is over the axes and if data is loaded
        if self.thermal_data_fahrenheit is None:
            return
        if event.inaxes == self.axis:
            col = int(event.xdata)
            row = int(event.ydata)
            if 0 <= col < self.thermal_data_fahrenheit.shape[1] and \
               0 <= row < self.thermal_data_fahrenheit.shape[0]:
                temp_value = self.thermal_data_fahrenheit[row, col]
                self.temp_label.set_text(f"{temp_value:.2f} °F")
                self.canvas.draw_idle()
            else:
                self.temp_label.set_text('')
                self.canvas.draw_idle()

    def update_slider_range(self):
        """Update the slider's range and colorbar based on user input."""
        self.slider_min_value = self.min_spinbox.value()
        self.slider_max_value = self.max_spinbox.value()
        self.range_slider.setRange(self.slider_min_value,
                                   self.slider_max_value)
        self.update_image()

    def show_dialog(self):
        """Open a file dialog and load the selected IRG file."""
        cwd = os.getcwd()
        fname, _ = QFileDialog.getOpenFileName(self, 'Open file', cwd)
        if fname:
            self.load_irg(fname)

    def load_irg(self, filepath):
        """Load and process the IRG file."""
        extracted_data = extract_data_from_binary(filepath)
        self.thermal_data = extracted_data["thermal_data"] / 10.0
        self.thermal_data_fahrenheit = (self.thermal_data - 273.15) * 9/5 + 32

        # Set the min/max values for the spin boxes and the range slider
        self.min_spinbox.setValue(self.thermal_data_fahrenheit.min())
        self.max_spinbox.setValue(self.thermal_data_fahrenheit.max())
        self.range_slider.setRange(self.thermal_data_fahrenheit.min(),
                                   self.thermal_data_fahrenheit.max())
        self.range_slider.setValue((self.thermal_data_fahrenheit.min(),
                                    self.thermal_data_fahrenheit.max()))
        self.update_image()
        self.image_loaded = True

    def update_image(self):
        """Updates the Image after we make any changes"""
        # Save current axis limits
        if self.image_loaded:
            x_min, x_max = self.axis.get_xlim()
            y_min, y_max = self.axis.get_ylim()
        value_min, value_max = self.range_slider.value()

        self.axis.clear()
        im = self.axis.imshow(self.thermal_data_fahrenheit,
                              cmap='inferno', vmin=value_min, vmax=value_max)

        # Set the color limits for the image
        im.set_clim(value_min, value_max)

        # Add colorbar and update its limits
        if hasattr(self, 'cbar'):
            self.cbar.remove()
        self.cbar = self.figure.colorbar(im, ax=self.axis)
        if self.image_loaded:
            self.axis.set_xlim(x_min, x_max)
            self.axis.set_ylim(y_min, y_max)
        self.canvas.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ThermalImageApp()
    sys.exit(app.exec_())
