# Google Analytics Client

Google analytics Report API v4 for Python3



## Example

```python
from client import GoogleAnalyticsClient

cli = GoogleAnalyticsClient(
    json_file="yourfile.json",
    view_id="XXXXXXXX",
    start_date="2021-01-01",
    end_date="2021-06-01",
)
response = cli.fetch_all(
  	dimensions=["ga:DateHourMinute"],
  	metrics=["ga:users", "ga:pageviews"]
)
```
