# Quick Start

### Install
```python
pip install devsetgo-lib
```

### Simple Use
#### Create Sample Data
Result will be in ***/data/csv*** and ***/data/json*** folders
```python

from devsetgo_lib.file_functions import create_sample_files

create_sample_files("test_file", sample_size=1000)
```

#### Create and open a CSV file
Result will be in ***/data/csv*** folder
```python

from devsetgo_lib.file_functions import save_csv, open_csv
data = [['num','1','2','3'],
        [f'{i}',"a","b","c"]]

save_csv("test.csv", data)

result =  open_csv("test.csv")
print(result)
```

#### Create and open a JSON file
Result will be in ***/data/csv*** folder
```python

from devsetgo_lib.file_functions import save_json, open_json

json_data = {"name": "John", "age": 30, "cars": ["Ford", "BMW", "Fiat"]}
    file_functions.save_json("test.json",json_data)

result = open_json("test.json")
print(result)
```

#### Create and open a Text file
Result will be in ***/data/text*** folder
```python

from devsetgo_lib.file_functions import save_text, open_text

html = """
<!DOCTYPE html>
<html>
<body>

<h1>My First Heading</h1>
<p>My first paragraph.</p>

</body>
</html>
"""

file_functions.save_text("test.html", html)

result = open_text("test.json")
print(result)
```