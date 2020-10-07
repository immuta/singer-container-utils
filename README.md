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
