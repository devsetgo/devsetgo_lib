# csv_example_with_timer Example

# CSV Example with Timer

This module demonstrates how to generate and save CSV files at regular intervals using Python.
It includes functionality to create sample data, save it to a CSV file, and repeat the process
indefinitely with a specified delay.

## Features

- **Dynamic Data Generation**: The `create_sample_list` function generates a list of lists
  with a customizable number of rows. Each row contains sample data with predefined headers.

- **Automated File Saving**: The `save_data_with_timer` function saves the generated data
  to a CSV file every 5 seconds. Each file is uniquely named with a timestamp to avoid
  overwriting.

- **Customizable CSV Format**: The CSV files are saved with a pipe (`|`) as the delimiter
  and double quotes (`"`) as the quote character.

- **Logging Support**: The module uses a logging configuration to provide debug-level
  logging for better traceability.

## Use Case

This module is ideal for scenarios where continuous data generation and saving are required,
such as testing, simulations, or data pipeline prototyping.

## Directory Structure

The generated CSV files are saved in the following directory:
```
/workspaces/devsetgo_lib/data/move/source
```

## How to Run

To execute the script, simply run it as a standalone program:
```bash
python csv_example_with_timer.py
```

The script will continuously generate and save CSV files until manually stopped.

## Dependencies

- `dsg_lib.common_functions.file_functions.save_csv`: A utility function to save data to a CSV file.
- `dsg_lib.common_functions.logging_config.config_log`: A utility function to configure logging.

## License
This module is licensed under the MIT License.

```python
import random
import time
from datetime import datetime

from dsg_lib.common_functions.file_functions import save_csv
from dsg_lib.common_functions.logging_config import config_log

config_log(logging_level="DEBUG")

example_list = [
    ["thing_one", "thing_two"],
    ["a", "b"],
    ["c", "d"],
    ["e", "f"],
    ["g", "h"],
]


def create_sample_list(qty=10):
    """
    Create a sample list of lists with specified quantity.
    """
    headers = ["thing_one", "thing_two", "thing_three", "thing_four", "thing_five"]
    sample_list = [headers]
    for i in range(qty):
        sample_list.append(
            [f"item_{i+1}", f"item_{i+2}", f"item_{i+3}", f"item_{i+4}", f"item_{i+5}"]
        )
    return sample_list


def save_data_with_timer():
    """
    Saves a new CSV file every 5 seconds with a unique timestamped name.

    This function generates a sample list of data with a random number of rows
    (between 10 and 100,000) using the `create_sample_list` function. It then
    saves this data to a CSV file in the specified directory. The file name
    includes a timestamp to ensure uniqueness. The CSV file is saved with a
    pipe (`|`) as the delimiter and double quotes (`"`) as the quote character.

    The process repeats indefinitely, with a 5-second delay between each file
    creation. This function is useful for testing or simulating scenarios where
    data is continuously generated and saved to disk.

    The saved files are stored in the `/workspaces/devsetgo_lib/data/move/source`
    directory.
    """
    while True:
        example_list = create_sample_list(qty=random.randint(10, 100000))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"data_{timestamp}.csv"
        save_csv(
            file_name=file_name,
            data=example_list,
            root_folder="/workspaces/devsetgo_lib/data/move/source",
            delimiter="|",
            quotechar='"',
        )
        print(f"Saved file: {file_name}")
        time.sleep(5)


if __name__ == "__main__":
    save_data_with_timer()
```
