import pandas as pd
import pathlib
import json
from typing import Union
import logging

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


@pd.api.extensions.register_dataframe_accessor("singer")
class SingerSpec:
    def __init__(self, df):
        self._df = df

    def export(
        self,
        stream: Union[None, str] = None,
        primary_key: Union[None, str] = None,
        file_name: Union[None, str] = None,
    ):
        """
        Transforms DataFrame to singer records.
        """
        parsed = self.parse_df_to_json()
        schema = self.get_tap_schema(stream, primary_key, parsed)
        records = self.get_tap_records(stream, parsed)
        output = [json.dumps(x) for x in [schema] + records]

        if file_name:
            LOGGER.info("Saving output to file.")
            pathlib.Path(file_name).write_text("\n".join(output))
        else:
            LOGGER.info("Logging to STDOUT.")
            print("\n".join(output))

        return output

    def parse_df_to_json(self):
        result = self._df.to_json(orient="table", index=None)
        parsed = json.loads(result)
        return parsed

    def get_tap_schema(self, stream_name, primary_key, parsed):
        tap_schema = {
            "type": "SCHEMA",
            "stream": stream_name,
            "key_properties": [primary_key],
            "schema": {"type": "object", "properties": {}},
        }
        properties = tap_schema["schema"]["properties"]
        for ii in parsed["schema"]["fields"]:
            field = ii["name"].replace(".", "__")
            properties[field] = {"type": ii["type"]}
        return tap_schema

    def get_tap_records(self, stream_name, parsed):
        records = []
        for ii in parsed["data"]:
            record = {
                "type": "RECORD",
                "stream": stream_name,
                "record": {k.replace(".", "__"): v for k, v in ii.items()},
            }
            records.append(record)
        return records
