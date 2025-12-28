import time
from datetime import datetime, timezone

s = "2025.12.28.14.45.00"
dt = datetime.strptime(s, "%Y.%m.%d.%H.%M.%S")
ts = dt.timestamp()

print(ts, time.time())
1766922300
1766922304