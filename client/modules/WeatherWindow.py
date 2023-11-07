from PyQt5.QtWidgets import QHBoxLayout, QWidget

from modules import server
from modules.weather_item import weather_item


class Weather:
    def __init__(self, weather_json):
        """
        Initializes a new instance of the class.

        Parameters:
            weather_json (dict): The JSON object containing weather data.

        Returns:
            None
        """
        self.times = weather_json['hourly']['time']
        self.temps = weather_json['hourly']['temperature_2m']
        self.hums = weather_json['hourly']['relativehumidity_2m']
        self.prob = weather_json['hourly']['precipitation_probability']

        self.data = list(zip(self.times, self.temps, self.hums, self.prob))


class WeatherWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self, period, server: server):
        super().__init__()
        layout = QHBoxLayout(self)
        self.setGeometry(300, 300, 350*period, 1000)
        self.setWindowTitle("Weather")
        data = server.get_weather()
        for day in range(period):
            layout.addWidget(weather_item(Weather(data), day))
        self.setLayout(layout)