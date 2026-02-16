import requests

# Get today's bills
response = requests.get('http://localhost:5000/api/credit/history?date_range=today')
data = response.json()

print("Current bill statuses:")
for bill in data['bills']:
    print(f"{bill['bill_number']} - {bill['payment_status']}")