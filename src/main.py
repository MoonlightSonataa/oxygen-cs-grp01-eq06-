# main.py
import json
import logging
import time
import yaml
import requests

from signalrcore.hub_connection_builder import HubConnectionBuilder


class Main:
    def __init__(self):
        self._hub_connection = None

        with open("config.yml", "r", encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file)

        self.host = config.get("variables", {}).get("HOST", "http://34.95.34.5")
        self.token = config.get("variables", {}).get("TOKEN")
        self.tickets = config.get("variables", {}).get("TICKETS", "5")
        self.t_max = config.get("variables", {}).get("T_MAX", "600")
        self.t_min = config.get("variables", {}).get("T_MIN", "2")
        self.database = config.get("variables", {}).get("DATABASE", "oxygenDB")

        print(f"TOKEN: '{self.token}'")

        self.validate_token()

    def __del__(self):
        if self._hub_connection is not None:
            self._hub_connection.stop()

    def setup(self):
        self.set_sensor_hub()

    def start(self):
        self.setup()
        self._hub_connection.start()

        print("Press CTRL+C to exit.")
        while True:
            time.sleep(2)

    def set_sensor_hub(self):
        self._hub_connection = (
            HubConnectionBuilder()
            .with_url(f"{self.host}/SensorHub?token={self.token}")
            .configure_logging(logging.INFO)
            .with_automatic_reconnect(
                {
                    "type": "raw",
                    "keep_alive_interval": 10,
                    "reconnect_interval": 5,
                    "max_attempts": 999,
                }
            )
            .build()
        )

        self._hub_connection.on("ReceiveSensorData", self.on_sensor_data_received)
        self._hub_connection.on_open(lambda: print("||| Connection opened."))
        self._hub_connection.on_close(lambda: print("||| Connection closed."))
        self._hub_connection.on_error(
            lambda data: print(f"||| An exception was thrown closed: {data.error}")
        )

    def on_sensor_data_received(self, data):
        try:
            print(data[0]["date"] + " --> " + data[0]["data"])
            date = data[0]["date"]
            date_dataa = float(data[0]["data"])
            self.send_temperature_to_fastapi(date, date_dataa)
            self.analyze_datapoint(date, date_dataa)
        except IndexError as err:
            print(err)

    def analyze_datapoint(self, date, data):
        if float(data) >= float(self.t_max):
            self.send_action_to_hvac(date, "TurnOnAc", self.tickets)
        elif float(data) <= float(self.t_min):
            self.send_action_to_hvac(date, "TurnOnHeater", self.tickets)

    def send_action_to_hvac(self, date, action, nb_tick):
        request = requests.get(
            f"{self.host}/api/hvac/{self.token}/{action}/{nb_tick}",
            timeout=5,
        )
        details = json.loads(request.text)
        print(str(details) + " date" + date)

    def send_temperature_to_fastapi(self, timestamp, temperature):
        try:
            payload = {"timestamp": timestamp, "temperature": temperature}
            response = requests.post(
                f"{self.host}/api/temperature",
                json=payload,
                timeout=5,
            )
            if response.status_code == 200:
                print("Temperature data sent to FastAPI successfully.")
            else:
                print(
                    f"Failed to send temperature data. Response code: {response.status_code}"
                )
        except requests.RequestException as err:
            print(f"Error sending temperature data to FastAPI: {err}")

    def validate_token(self):
        """
        Validate the token environment variable.

        This method checks if the TOKEN environment variable is defined and not empty.
        If the token is missing or empty, it raises a ValueError.
        """
        print("Validating token...")
        print(f"Token: '{self.token}'")
        if not self.token or not self.token.strip():
            print("Token is missing or empty.")
            raise ValueError("TOKEN is not defined or empty in the configuration file.")
        else:
            print("test: Token is valid.")


if __name__ == "__main__":
    main = Main()
    main.start()
