import requests


class Server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.weatherAPI = "https://api.open-meteo.com/v1/forecast?latitude=51.672&longitude=39.1843&current=temperature_2m,relativehumidity_2m&hourly=temperature_2m,relativehumidity_2m,precipitation_probability&timezone=Europe%2FMoscow"

    def get_data(self):
        """
        Retrieves data from the server.

        Returns:
            The data retrieved from the server as a JSON object.
            If there is an error getting the data, returns -1.
        """
        req = requests.get(f"http://{self.ip}:{self.port}/get_state")
        if req.status_code == 200:
            return req.json()
        else:
            print("Error getting data from server #{}".format(req.status_code))
            return -1
            
        
    def set_data(self, data):
        req = requests.post(f"http://{self.ip}:{self.port}/set_state", data=data, headers={"Content-Type": "application/json"})
        return req.status_code
    

    def get_history(self, count):
        req = requests.get(f"http://{self.ip}:{self.port}/get_history?count={count}")
        return req.json()

    def get_database(self):
        req = requests.get(f"http://{self.ip}:{self.port}/log-download")
        if req.status_code == 200:
            return req.content
        else:
            print("Error getting data from server #{}".format(req.status_code))
            return -1
    
    def get_weather(self):
        req = requests.get(self.weatherAPI)
        data = req.json()
        return data