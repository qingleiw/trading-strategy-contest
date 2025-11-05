"""Clean ETH CSV file - remove duplicates and sort"""

import csv
from datetime import datetime

# Read the CSV
rows = []
seen = set()

with open('ETH-USD_2024_Jan-Jun.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Create unique key from timestamp
        key = row['timestamp']
        if key not in seen:
            seen.add(key)
            rows.append(row)

# Sort by timestamp
rows.sort(key=lambda x: datetime.strptime(x['timestamp'], '%Y-%m-%d %H:%M:%S'))

# Write back
with open('ETH-USD_2024_Jan-Jun.csv', 'w', newline='') as f:
    if rows:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

print(f"✅ Cleaned: {len(rows)} unique rows")
print(f"📅 Range: {rows[0]['timestamp']} to {rows[-1]['timestamp']}")

# Check if we have Jan 1 data
first_date = datetime.strptime(rows[0]['timestamp'], '%Y-%m-%d %H:%M:%S')
if first_date.month > 1 or first_date.day > 1:
    print(f"⚠️  Warning: Data starts from {rows[0]['timestamp']}, not Jan 1, 2024")
else:
    print("✅ Data starts from January 2024")
