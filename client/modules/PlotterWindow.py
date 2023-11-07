import pyqtgraph as pg
from PyQt5.QtCore import QTimer
uiclass, baseclass = pg.Qt.loadUiType("ui/graph.ui")

COUNT = 60 * 24

class PlotterWindow(uiclass, baseclass):

    def __init__(self, what, server):
        super().__init__()
        self.setupUi(self)
        self.server = server
        self.what = what
        self.plot()
        
        self.setWindowTitle("Data Plotter")
        
        
        self.update_timer = QTimer() 
        self.update_timer.timeout.connect(self.plot)
        self.update_timer.start(15000)
        self.update_timer.start()
    
    def plot(self):
        """
        Plot the graph based on the data retrieved from the server.

        Parameters:
            None

        Returns:
            None
        """
        self.graphWidget.clear()
        num = COUNT * 4
        data = self.server.get_history(num)
        if self.what == "hum":
            y = [data.get(str(i))[2] for i in range(num) if i % 4 ==0][::-1]
            x = [":".join(data.get(str(i))[0].split(" ")[1].split(":")[:2]) for i in range(num) if i % 4 ==0][::-1]
        elif self.what == "temp":
            y = [data.get(str(i))[1] for i in range(num) if i % 4 ==0][::-1]
            x = [":".join(data.get(str(i))[0].split(" ")[1].split(":")[:2]) for i in range(num) if i % 4 ==0][::-1]


        
        pen = pg.mkPen(color=(255, 0, 0))

        time_labels = [
            # Generate a list of tuples (x_value, x_label)
            (m, x[m])
            for m in range(len(x))
        ]
        self.graphWidget.plot(range(len(x)), y, pen=pen, labels=time_labels)
        ax = self.graphWidget.getAxis('bottom')
        ax.setTicks([time_labels])
    