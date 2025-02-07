# main.py
import json
import logging
import time
import yaml
import requests
import psycopg2

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
        
        
    def send_temperature_to_postgres(self, timestamp, temperature):
        try:
            conn = psycopg2.connect(
                # host="35.192.151.166",  # your database host    # for dev usage
                host="localhost",   # for deployment only
                database="LOG680_DEVOPS",  # your database name
                user="postgres",  # your database username
                password="postgres"  # your database password
            )
            cur = conn.cursor()

            query = """
            INSERT INTO temperature_logs (log_time, temperature) 
            VALUES (%s, %s)
            """
            cur.execute(query, (timestamp, temperature))

            conn.commit()
            cur.close()
            conn.close()

            print("Temperature data sent to DB successfully.")
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error sending temperature data to DB: {error}")

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
            self.send_temperature_to_postgres(date, date_dataa)  # replace this line
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



    def send_temperature_to_db(self, timestamp, temperature):
        try:
            # Connect to your postgres DB
            conn = psycopg2.connect(
                dbname="LOG680_DEVOPS",
                user="postgres",
                password="postgres",
                # host="35.192.151.166",    # for dev usage
                host="localhost",   # for deployment only
            )

            # Open a cursor to perform database operations
            cur = conn.cursor()

            # Execute a query
            cur.execute("INSERT INTO temperature_logs (log_time, temperature) VALUES (%s, %s)", (timestamp, temperature))

            # Commit the transaction
            conn.commit()

            # Close the cursor and connection
            cur.close()
            conn.close()

            print("Temperature data sent to DB successfully.")

        except Exception as e:
            print(f"Failed to send temperature data to DB. Error: {str(e)}")


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
