# Calendar Functions

### TODO:
- none


### Get Month

***get_month(month: int) -> str:***

Pass in month integer value and get back string name of month (e.g. January, February, etc.). An integer value of 1-12 will work, any other values are invalid.

In this example '0' and '13' will return "Invalid month number" as a response.

```python
from devsetgo_lib.calendar_functions import get_month

month_list:list=[0,1,2,3,4,5,6,7,8,9,10,11,12,13]

def calendar_check():
    for i in month_list:
        month=get_month(month=i)
        print(month)

```

