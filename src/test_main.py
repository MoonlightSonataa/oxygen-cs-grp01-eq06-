import os
import sys
import unittest
import yaml
from unittest.mock import patch, Mock

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from main import Main


class MainTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "config_test.yml"
        )
        with open(config_file, "r", encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file)
        os.environ.update(config.get("variables", {}))


    def test_default_values(self):
        with patch.dict("os.environ", {}):
            main = Main()
            self.assertEqual(main.host, "http://34.95.34.5")
            self.assertEqual(main.tickets, "5")
            self.assertEqual(main.t_max, "600")
            self.assertEqual(main.t_min, "2")
            self.assertEqual(main.database, "oxygenDB")

    def test_env_values(self):
        with patch.dict(
            "os.environ",
            {
                "HOST": "http://34.95.34.5",
                "TOKEN": "69aWxpk655",
                "TICKETS": "5",
                "T_MAX": "600",
                "T_MIN": "2",
                "DATABASE": "oxygenDB",
            },
        ):
            main = Main()
            self.assertEqual(main.host, "http://34.95.34.5")
            self.assertEqual(main.token, "69aWxpk655")
            self.assertEqual(main.tickets, "5")
            self.assertEqual(main.t_max, "600")
            self.assertEqual(main.t_min, "2")
            self.assertEqual(main.database, "oxygenDB")

    def test_missing_token(self):
        with patch.dict(
            "os.environ",
            {
                "HOST": "http://34.95.34.5",
                "TOKEN": "",
                "TICKETS": "5",
                "T_MAX": "600",
                "T_MIN": "2",
                "DATABASE": "oxygenDB",
            },
        ):
            try:
                Main()
            except ValueError as err:
                print(f"Caught exception: {err}")
                raise err


    @patch("requests.get")
    def test_analyze_datapoint_above_max(self, mock_get):
        main = Main()
        mock_get.return_value = Mock(text='{"result": "success"}')
        main.t_max = "30"
        main.analyze_datapoint("2023-07-02T12:00:00Z", "35")
        mock_get.assert_called_once_with(
            f"{main.host}/api/hvac/{main.token}/TurnOnAc/{main.tickets}",
            timeout=5,
        )

    @patch("requests.get")
    def test_analyze_datapoint_below_min(self, mock_get):
        main = Main()
        mock_get.return_value = Mock(text='{"result": "success"}')
        main.t_min = "20"
        main.analyze_datapoint("2023-07-02T12:00:00Z", "15")
        mock_get.assert_called_once_with(
            f"{main.host}/api/hvac/{main.token}/TurnOnHeater/{main.tickets}",
            timeout=5,
        )

    @patch("requests.get")
    def test_analyze_datapoint_in_range(self, mock_get):
        main = Main()
        mock_get.return_value = Mock(text='{"result": "success"}')
        main.t_min = "20"
        main.t_max = "30"
        main.analyze_datapoint("2023-07-02T12:00:00Z", "25")
        mock_get.assert_not_called()


if __name__ == "__main__":
    unittest.main()
