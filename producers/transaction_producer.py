from kafka import KafkaProducer
import json
import time
import random
import uuid
from datetime import datetime

# Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print("Producing random transactions...")

transaction_types = ["withdrawal", "deposit", "transfer", "online_payment"]
locations = ["ATM_001", "ATM_123", "ATM_999", "Store_567", "Mall_202", "POS_404"]

MAX_TXNS = 10
count=0
while count < MAX_TXNS:
    # Generate a random transaction
    transaction_data = {
        "user_id": f"user_{random.randint(1, 50)}",
        "transaction_id": str(uuid.uuid4()),
        "amount": random.randint(100, 20000),   # random amount ₹100–₹20,000
        "transaction_type": random.choice(transaction_types),
        "location": random.choice(locations),
        "time": datetime.utcnow().isoformat()
    }

    # Print to console
    print("Produced Transaction →", transaction_data)

    # Send to Kafka topic
    producer.send("transaction-events", value=transaction_data)
    producer.flush()

    count += 1
    time.sleep(1)  # produce one transaction per second
