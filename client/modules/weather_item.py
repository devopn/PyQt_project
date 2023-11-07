from PyQt5.QtWidgets import QWidget
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore


class weather_item(QWidget):
    def __init__(self, weather, day):
        """
        Initializes the weather view for a specific day.

        Args:
            weather (Weather): The weather object containing the data.
            day (int): The index of the day to display.

        Returns:
            None
        """
        super().__init__()

        lay = QtWidgets.QVBoxLayout(self)

        self.listView = QtWidgets.QListView()
        lay.addWidget(self.listView)

        self.entry = QtGui.QStandardItemModel()
        self.listView.setSpacing(5)
        self.entry.appendRow(QtGui.QStandardItem("                 Date                   //  Temp  /  Hum "))

        for item in weather.data[day*24:(day+1)*24]:
            month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            date = item[0].split("T")
            d = date[0].split("-")
            it = QtGui.QStandardItem(f"{date[1]} // {d[2]} {month[int(d[1]) - 1]} {d[0]} : {item[1]}\u00b0C, {item[2]}%")
            # print(item)
            self.entry.appendRow(it)
            
            if int(item[3]) > 20:
                it.setData(QtGui.QIcon("media/rain.png"), QtCore.Qt.DecorationRole)
            else:
                it.setData(QtGui.QIcon("media/sunny-day.png"), QtCore.Qt.DecorationRole)

        self.listView.setModel(self.entry) 
