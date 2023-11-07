from flask import Flask, request, jsonify
import sqlite3
import json
from flask import send_file
app = Flask(__name__)


def save_state(state):
    """
    Save the current state to a JSON file.

    Args:
        state (Any): The current state to be saved.

    Returns:
        None
    """
    with open(".current_state.json ", "w") as file:
        json.dump(state, file)


try:
    with open("data/.current_state.json ", "r") as file:
        actual_state = json.load(file)
except:
    with open("data/.current_state.json ", "w") as file:
        actual_state = {"temp": 0, "hum": 0, "color": "FFFFFF"}
        json.dump(actual_state, file)

@app.route("/")
def default():
    return {"it":"works"}

@app.route("/get_state")
def get_state():
    return actual_state

@app.route("/get_history", methods=["GET"])
def get_history():
    """
    Retrieves the history of sensor data.

    This function is used to retrieve the history of sensor data from the database. It expects a HTTP GET request to the '/get_history' endpoint. The function retrieves the specified number of records from the 'sensors' table in the 'home_sensors_log.sqlite' database, ordered by the 'id' column in descending order. The retrieved data is then converted into a dictionary where the keys are the indices of the records and the values are tuples containing the datetime, temperature, and humidity values. The resulting dictionary is then converted to JSON format using the 'jsonify' function and returned as the response.

    Parameters:
    - count (int): The number of records to retrieve from the database.

    Returns:
    - Response: A JSON response containing the history of sensor data.

    Example Usage:
    ```
    GET /get_history?count=10
    ```

    Response:
    ```
    {
        "0": ["2022-01-01 12:00:00", 25.5, 60.0],
        "1": ["2022-01-01 12:01:00", 26.0, 58.5],
        ...
    }
    ```
    """
    count = request.args.get("count")
    con = sqlite3.connect("data/home_sensors_log.sqlite")
    data = con.execute(
        """SELECT datetime, temp, hum FROM sensors ORDER BY id DESC LIMIT 0,?;""", (count,)
    ).fetchall()
    con.close()
    result = dict()
    for i in range(len(data)):
        result[i] = data[i]
    return jsonify(result)

@app.route("/set_state", methods=["POST"])
def set_state():
    """
    Sets the state of the application based on the data received in the request.

    Parameters:
    - None

    Returns:
    - dict: The updated state of the application.

    Raises:
    - None
    """
    data = request.json
    for i in data:
        if data[i] != -1:
            actual_state[i] = data[i]
    save_state(actual_state)

    con = sqlite3.connect("data/home_sensors_log.sqlite")
    cur = con.cursor()
    data = cur.execute(
        """INSERT INTO sensors(datetime, temp, hum) VALUES(datetime('now', '+180 minutes'), ?, ?)""", (actual_state['temp'], actual_state['hum'])
    )
    con.commit()
    con.close()

    return actual_state

@app.route('/log-download')
def log_download():
    """
    Download the log file.

    :return: The log file.
    :rtype: File
    """
    try:
        return send_file("data/home_sensors_log.sqlite")
    except Exception as e:  
        return str(e)
    

if __name__ == "__main__":
    try:
        app.run(debug=True)
    except:
        save_state(actual_state)