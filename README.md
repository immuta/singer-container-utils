# Singer Container Utilities

This is a simple utility library for easing the creation of Docker containers
leveraging [Singer.io](https://singer.io) taps and targets.

Install it by running:

```{zsh}
pip install https://github.com/immuta/singer-container-utilities/archive/master.zip
```

## Examples

`sample_entrypoint.py` has an example implementation of this package for a tap.
In its simplest form, the user simply needs to specify the tap command, the available
configuration keys, and the path to the output. When the tap runs, it will save the
output to a specific file location, which can then be mapped to a target container,
e.g. in Argo.

```{python}
from singer_container_utils import TapRunner

tap = TapRunner(
    execute_command="tap-exchangeratesapi",
    required_config_keys=["start_date"],
    path_to_output="/tmp/tap_output.txt",
    discover_catalog=False,
)
tap.run()
```


### Pandas Singer Namespace

This package also adds a lightweight Singer namespace to Pandas DataFrames, which enable exporting of any `pd.DataFrame` to Singer records. 

```{python}
# t.py
import pandas as pd
import singer_container_utils

d = {"a": [1, 2], "b": [3, 4]}
df = pd.DataFrame(d)
output = df.singer.export(stream="test", primary_key="a")
```

```{shell}
$ python t.py 
{"type": "SCHEMA", "stream": "test", "key_properties": ["a"], "schema": {"type": "object", "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}}}}
{"type": "RECORD", "stream": "test", "record": {"a": 1, "b": 3}}
{"type": "RECORD", "stream": "test", "record": {"a": 2, "b": 4}}
```