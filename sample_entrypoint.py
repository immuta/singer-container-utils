"""
This script runs the Tap-ExchangeRatesApi tap, if installed,
and outputs the contents to /tmp/tap_output.txt
"""


import os
from singer_container_utils import TapRunner

os.environ["START_DATE"] = "2020-09-01"

tap_configs = dict(
    execute_command="tap-exchangeratesapi",
    required_config_keys=["start_date"],
    path_to_output="/tmp/tap_output.txt",
    discover_catalog=False,
)

if __name__ == "__main__":
    tap = TapRunner(**tap_configs)
    tap.run()
