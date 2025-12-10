from kafka import KafkaConsumer
import json

def send_alert(alert):
    print("\nEMAIL ALERT (simulated):")
    print(f"Alert for User: {alert.get('user_id')}")
    print(f"Transaction ID: {alert.get('transaction_id')}")
    print(f"Amount: {alert.get('amount')}")   
    print("Suspicious transaction detected!")

consumer = KafkaConsumer(
    'fraud-alerts',
    bootstrap_servers='localhost:9092',
    group_id='notification-service',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("Listening for fraud alerts...")

for message in consumer:
    alert = message.value
    print("\nReceived fraud alert:", alert)
    send_alert(alert)
