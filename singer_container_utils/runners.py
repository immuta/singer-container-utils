import json
import logging
import os
import pathlib
import subprocess
import sys


logging.basicConfig(level=logging.INFO)


class TapRunner:
    """
    The TapRunner is a configurable object for running singer.io taps. It is
    intended to facilitate the re-use of an entrypoint script across Argo
    workflows.
    """

    config = None
    catalog = None
    state = None

    def __init__(
        self,
        execute_command: str,
        required_config_keys: list = [],
        path_to_config: str = "/tmp/config.json",
        path_to_catalog: str = "/tmp/catalog.json",
        path_to_state: str = "/tmp/state.json",
        path_to_output: str = "/tmp/tap_output.txt",
        discover_catalog: bool = True,
    ) -> None:

        self.execute_command = execute_command
        self.required_config_keys = required_config_keys
        self.config_file = pathlib.Path(path_to_config)
        self.catalog_file = pathlib.Path(path_to_catalog)
        self.state_file = pathlib.Path(path_to_state)
        self.output_file = pathlib.Path(path_to_output)

        self.write_config()

        if not self.catalog_file.exists() and discover_catalog:
            logging.info("No catalog provided. Generating catalog via discovery mode.")
            self.discover_catalog()

    def write_config(self, use_environment=True, validate_keys=True) -> None:
        """The tap has two methods for running:
        1. if there is a "config.json" file mapped to the working directory,
           it will use that as a base
        2. if matching environment variables are present, it will override the config file
        It will run a check of all required "config_keys" are present, it will generate the file."""

        config_from_file = {}
        if self.config_file.exists():
            config_from_file = json.loads(self.config_file.read_text())

        config_from_env = {}
        if use_environment:
            config_from_env = {
                v: os.environ.get(v.lower(), os.environ.get(v.upper()))
                for v in self.required_config_keys
                if os.environ.get(v.lower(), os.environ.get(v.upper()))
            }

        config = {**config_from_file, **config_from_env}

        if validate_keys:
            missing = [
                var for var in self.required_config_keys if var not in config.keys()
            ]
            if any(missing):
                raise KeyError(f"Missing required key(s): {missing}")

        self.config_file.write_text(json.dumps(config))

    def discover_catalog(self):
        "Runs the tap in discovery mode and save to the catalog file"

        cmd = [
            self.execute_command,
            "--config",
            self.config_file.as_posix(),
            "--discover",
        ]
        catalog_process = subprocess.run(cmd, capture_output=True)
        self.catalog_file.write_text(catalog_process.stdout.decode("utf-8"))

    def make_command(self, use_properties = False):
        "Create the tap command using the available config files."
        command = [self.execute_command]

        if self.config_file.exists():
            command.extend(["--config", self.config_file.as_posix()])
        if self.catalog_file.exists():
            arg = "--properties" if use_properties else "--catalog"
            command.extend([arg, self.catalog_file.as_posix()])
        if self.state_file.exists():
            command.extend(["--state", self.state_file.as_posix()])

        return command

    def run(self, use_properties=False):
        tap_command = self.make_command(use_properties)

        logging.info("Running tap command: %s", " ".join(tap_command))
        with open(self.output_file, "w") as f:
            proc = subprocess.Popen(tap_command, stdout=subprocess.PIPE)
            for line in proc.stdout:
                f.write(line.decode("utf-8"))
            proc.wait()

            if proc.returncode != 0:
                sys.exit(1)
        logging.info("Finished running tap.")



class TargetRunner:
    """
    The TargetRunner is a configurable object for running singer.io taps. It is
    intended to facilitate the re-use of an entrypoint script across Argo
    workflows.
    """

    config = None

    def __init__(
        self,
        execute_command: str,
        required_config_keys: list = [],
        optional_config_keys: list = [],
        path_to_config: str = "/tmp/config.json",
        path_to_input: str = "/tmp/tap_input.txt",
        path_to_output: str = "/tmp/target_output.txt",
    ) -> None:

        self.execute_command = execute_command
        self.required_config_keys = required_config_keys
        self.optional_config_keys = optional_config_keys
        self.config_file = pathlib.Path(path_to_config)
        self.input_file = pathlib.Path(path_to_input)
        self.output_file = pathlib.Path(path_to_output)

        self.write_config()

    def write_config(self, use_environment=True, validate_keys=True) -> None:

        config_from_file = {}
        if self.config_file.exists():
            config_from_file = json.loads(self.config_file.read_text())

        all_keys = {**self.required_config_keys, **self.optional_config_keys}
        config_from_env = {}
        if use_environment:
            config_from_env = {
                v: os.environ.get(v.lower(), os.environ.get(v.upper()))
                for v in all_keys
                if os.environ.get(v.lower(), os.environ.get(v.upper()))
            }

        config = {**config_from_file, **config_from_env}

        if validate_keys:
            missing = [
                var for var in self.required_config_keys if var not in config.keys()
            ]
            if any(missing):
                raise KeyError(f"Missing required key(s): {missing}")

        self.config_file.write_text(json.dumps(config))

    def make_command(self):
        "Create the tap command using the available config files."
        command = [self.execute_command]

        if self.config_file.exists():
            command.extend(["--config", self.config_file.as_posix()])

        return command

    def run(self):
        cmd = self.make_command()

        logging.info("Beginning load into target database.")
        with open(self.input_file, "r") as f_inp, open(self.output_file, "w") as f_out:
            proc = subprocess.Popen(cmd, stdin=f_inp, stdout=subprocess.PIPE,)
            for line in proc.stdout:
                f_out.write(line.decode("utf-8"))
            proc.wait()

            if proc.returncode != 0:
                sys.exit(1)
        logging.info("Finished running target.")