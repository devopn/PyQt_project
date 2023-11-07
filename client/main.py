# http://146.0.79.198:5000/get_state

import sys
import json
import PyQt5
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QInputDialog
import datetime
from PyQt5.QtCore import QTimer
from modules.server import Server
from modules.PlotterWindow import PlotterWindow
from modules.WeatherWindow import WeatherWindow
from PyQt5.QtGui import QMovie

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class SmartHomeWidget(QMainWindow):
    lastTenTemp = []
    lastTenHum = []

    def __init__(self):
        super().__init__()
        uic.loadUi("ui/app.ui", self)
        # INIT SERVER
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                self.server = Server(config["ip"], config["port"])
        except:
            print("Error initializing server")
            exit()

        # Connect color sliders to button
        self.slider_blue.valueChanged.connect(self.change_button_color)
        self.slider_green.valueChanged.connect(self.change_button_color)
        self.slider_red.valueChanged.connect(self.change_button_color)
        actual_data = self.get_data_from_server()
        if actual_data != -1:
            self.slider_red.setValue(int(actual_data["color"][0:2], 16))
            self.slider_green.setValue(int(actual_data["color"][2:4], 16))
            self.slider_blue.setValue(int(actual_data["color"][4:6], 16))
        self.update_data()

        # Set colors to server
        self.button_color_update.clicked.connect(self.set_color_to_server)

        # Create timer to update data
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.setInterval(self.freq_spin.value() * 1000)
        self.timer.start()
        self.freq_spin.valueChanged.connect(self.timer_setInterval)

        # Create timer to clock
        self.update_clock()
        self.clock = QTimer()
        self.clock.timeout.connect(self.update_clock)
        self.clock.start(1000)
        self.clock.start()

        # Connect graph buttons
        self.button_humidity_graph.clicked.connect(self.plote_hum)
        self.button_temperature_graph.clicked.connect(self.plote_temp)

        self.actionReset.triggered.connect(self.reset)
        self.actionget_logs.triggered.connect(self.get_log)

        self.actionToday.triggered.connect(self.show_weather_builder(1))
        self.actionTomorrow.triggered.connect(self.show_weather_builder(2))
        self.actionFor_5_days.triggered.connect(self.show_weather_builder(5))

        # init gifs
        self.updateArrow = QMovie("media/update.gif")
        self.hum_dynamic.setMovie(self.updateArrow)
        self.temp_dynamic.setMovie(self.updateArrow)
        self.updateArrow.start()

    def change_button_color(self):
        """
        Change the color of a button based on the values of three sliders.

        This function takes no parameters.

        It retrieves the current values of three sliders: `slider_red`, `slider_green`, and `slider_blue`.

        It calculates the hexadecimal representation of the RGB color using the retrieved slider values.

        It sets the background color of the `button_color_update` widget to the calculated color.

        It also calculates the contrast color of the text using the complement of the RGB color.

        The calculated color styles are concatenated into a single string `style`.

        Finally, the `button_color_update` widget is updated with the new style.

        This function does not return any value.
        """
        r = self.slider_red.value()
        g = self.slider_green.value()
        b = self.slider_blue.value()
        style = "background-color: #{:02X}{:02X}{:02X};".format(r, g, b)
        style += "color: #{:02X}{:02X}{:02X}".format(255 - r, 255 - g, 255 - b)
        # Set contrast color of text
        self.button_color_update.setStyleSheet(style)

    def get_data_from_server(self):
        """
        Retrieves data from the server.

        Parameters:
            self (object): The instance of the class.
        
        Returns:
            Any: The data retrieved from the server.
        """
        data = self.server.get_data()
        if data == -1:
            self.statusbar.showMessage("Error getting data from server")
        else:
            return data

    def set_data_to_server(self, data):
        """
        Sets the provided data to the server.

        Parameters:
        - data: The data to be set on the server.

        Returns:
        No return value.

        Raises:
        No exceptions are raised.
        """
        response_code = self.server.set_data(data)
        if response_code == 200:
            self.statusbar.showMessage("Success")
        else:
            self.statusbar.showMessage(
                "Error sending data to server #{}".format(response_code)
            )

    def set_color_to_server(self):
        """
        Set the color of the server.

        This function retrieves the RGB values from three sliders, converts them into a hexadecimal color code, and then sets the color of the server accordingly. The RGB values are obtained from the `slider_red`, `slider_green`, and `slider_blue` attributes of the class instance. These values are then formatted into a hexadecimal color code using the `format()` method.

        The function then calls the `get_data_from_server()` method to retrieve data from the server. If the data is successfully retrieved (i.e., not equal to -1), the function updates the `"color"` key in the data dictionary with the newly generated color. The updated data is then serialized into JSON format using the `json.dumps()` function. Finally, the function calls the `set_data_to_server()` method to send the updated data back to the server.

        Parameters:
        - None

        Returns:
        - None
        """
        r = self.slider_red.value()
        g = self.slider_green.value()
        b = self.slider_blue.value()
        color = "{:02X}{:02X}{:02X}".format(r, g, b)
        data = self.get_data_from_server()
        if data != -1:
            data["color"] = color
            self.set_data_to_server(json.dumps(data))

    def timer_setInterval(self):
        self.timer.setInterval(self.freq_spin.value() * 1000)

    def update_data(self):
        """
        Updates the data displayed on the GUI based on the data retrieved from the server.

        Parameters:
            None

        Returns:
            None
        """
        self.growArrow = QMovie("media/grow.gif")
        self.dropArrow = QMovie("media/drop.gif")
        self.updateArrow = QMovie("media/update.gif")
        
        data = self.get_data_from_server()
        if data != -1:
            temp = round(data["temp"], 1)

            self.lastTenTemp.append(temp)
            if len(self.lastTenTemp) > 10:
                self.lastTenTemp.pop(0)

            if sum(self.lastTenTemp) / len(self.lastTenTemp) > self.lastTenTemp[0]:
                self.temp_dynamic.setMovie(self.growArrow)
                self.growArrow.start()
            elif sum(self.lastTenTemp) / len(self.lastTenTemp) == self.lastTenTemp[0]:
                self.temp_dynamic.setMovie(self.updateArrow)
                self.updateArrow.start()
            else:
                self.temp_dynamic.setMovie(self.dropArrow)
                self.dropArrow.start()

            self.temperature_value.setText(str(temp) + "\u00b0C")
            hum = round(data["hum"], 1) 

            self.lastTenHum.append(hum)
            if len(self.lastTenHum) > 10:
                self.lastTenHum.pop(0)

            if sum(self.lastTenHum) / len(self.lastTenHum) > self.lastTenHum[0]:
                self.hum_dynamic.setMovie(self.growArrow)
                self.growArrow.start()
            elif sum(self.lastTenHum) / len(self.lastTenHum) == self.lastTenHum[0]:
                self.hum_dynamic.setMovie(self.updateArrow)
                self.updateArrow.start()
            else:
                self.hum_dynamic.setMovie(self.dropArrow)
                self.dropArrow.start()

            self.humidity_value.setText(str(hum) + "%")
            if (hum < 30) or hum > 60:
                self.humidity_value.setStyleSheet("color: red")
            else:
                self.humidity_value.setStyleSheet("color: green")

            if (temp < 18) or (temp > 28):
                self.temperature_value.setStyleSheet("color: red")
            else:
                self.temperature_value.setStyleSheet("color: green")
            self.statusbar.clearMessage()

    def update_clock(self):
        now = datetime.datetime.now()
        self.clock_label.setText(now.strftime("%H:%M:%S"))

    def plote_temp(self):

        self.win = PlotterWindow("temp", self.server)
        self.win.show()

    def plote_hum(self):

        self.win = PlotterWindow("hum", self.server)
        self.win.show()

    def get_log(self):
        name = QFileDialog.getSaveFileName(self, "Save logs")
        try:
            file = self.server.get_database()
            with open(name[0], "wb") as f:
                f.write(file)
        except Exception:
            print("Error getting data from server")

    def reset(self):
        """
        Resets the values of the humidity, temperature, and RGB sliders.

        Parameters:
            None

        Returns:
            None
        """
        self.humidity_value.setText("")
        self.temperature_value.setText("")
        self.slider_red.setValue(0)
        self.slider_green.setValue(0)
        self.slider_blue.setValue(0)

    def show_weather_builder(self, period):
        """
        A function that builds and returns a function to show the weather window.

        Parameters:
            period (str): The period for which the weather information is displayed.

        Returns:
            function: A function that shows the weather window when called.
        """
        def show():
            self.win = WeatherWindow(period, self.server)
            self.win.show()

        return show


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = SmartHomeWidget()
    ex.show()
    sys.exit(app.exec_())
