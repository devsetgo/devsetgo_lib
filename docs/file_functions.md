# File Functions

### TODO:
- Create configuration for library to specify custom configurations


### Create Sample Data

***create_sample_files(filename: str, sample_size: int)***

Pass in file name without an extension (.json or .csv) and the sample size. The function will create a CSV and JSON file with the resulting files in ***/data/csv*** and ***/data/json*** folders
```python

from dsg_libfile_functions import create_sample_files

create_sample_files(filename="test_file", sample_size=1000)
```

### Create and open a CSV file

### Save CSV
***save_csv(file_name="your-file-name.csv", data=example_list, root_folder="/data", delimiter=",", quotechar='"')***

Required fields are ***filename*** and ***data*** (must be a list).

Optional Fields:

- ***root_folder***: By default, the ***root_dir*** is **"data"**. The results will be in ***/data/csv*** folder, unless ***root_folder*** is defined.
- ***delimiter***: Default is ',', must be a single printable character
- ***quotechar***: Default is '"', must be a single printable character
=======

### Open CSV
***open_csv(filename: str, delimit: str = None)***

Required filed of filename and optional delimiter field (delimit=). Quoting is set to minimal and initial spaces will be skipped (removed). Output result is a dictionary/json object.

```python

from dsg_libfile_functions import save_csv, open_csv
data = [['num','1','2','3'],
        [f'{i}',"a","b","c"]]

save_csv(filename="test.csv", datad=data, root_folder=None, delimiter=None,  quotechar=None)

result =  open_csv(filename="test.csv")
print(result)
```
***Note:*** Data being sent is a list of lists. Each row in a csv is a list. So construct the data in a similar fashion as such. Otherwise the data will not persist as you expect.

```python
data = []
count = 1
header = ["column 1", "column 2", "column 3", "column 4"]
data.append(header)

for _ in range(10):
    row = ["this", "is", "row", numb]
    data.append(row)
    count += 1

```

### Create and open a JSON file

***save_json(filename: str, data: list, root_folder: str = None)***

Required fields are ***filename*** and ***data*** (must be a list). Optional is the ***root_folder***. By default, the ***root_dir*** is **"data"**. The results will be in ***/data/json*** folder, unless ***root_folder*** is defined.

***open_json(filename: str)***

Required filed of filename and optional delimiter field (delimit=). Quoting is set to minimal and initial spaces will be skipped (removed).
```python

from dsg_libfile_functions import save_json, open_json

json_data = {"name": "John", "age": 30, "cars": ["Ford", "BMW", "Fiat"]}

save_json(filename="test.json",data=json_data, root_folder="data")

result = open_json(filename="test.json")
print(result)
```

### Create and open a Text file

***save_text(filename: str, data: list, root_folder: str = None)***

Required fields are ***filename*** and ***data*** (must be a list). Optional is the ***root_folder***. By default, the ***root_dir*** is **"data"**. The results will be in ***/data/text*** folder, unless ***root_folder*** is defined.

***open_text(filename: str)***

Required filed of filename and output is a string. Output result will be in ***/data/text*** folder.
```python

from dsg_libfile_functions import save_text, open_text

html = """
<!DOCTYPE html>
<html>
<body>

<h1>My First Heading</h1>
<p>My first paragraph.</p>

</body>
</html>
"""

file_functions.save_text(filename="test.html", data=html)

result = open_text(filename="test.json")
print(result)
```

### Delete File

***delete_file(file_name: str)***

Required fields are ***filename***. Based on extension, the file will be removed. If the extension is other than .json or .csv, the file to removed will be removed from the data/text folder.

```python

from dsg_libfile_functions import delete_file

delete_file(filename="test.html", data=html)

```