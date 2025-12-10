# fraud_detection_consumer_ml.py
"""
ML-based Fraud Detection Consumer using IsolationForest pipeline.
Loads models/iforest_pipeline.joblib (StandardScaler+IsolationForest),
reads from 'transaction-events', scores transactions, and flags anomalies
when decision_function < ANOMALY_THRESHOLD.

Produces alerts to 'fraud-alerts' and stores flagged docs in MongoDB.
"""

import os
import json
import time
import traceback
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from kafka import KafkaConsumer, KafkaProducer, errors
from pymongo import MongoClient

# ---------- CONFIG ----------
BOOTSTRAP = "localhost:9092"
TOPIC_IN = "transaction-events"
TOPIC_OUT = "fraud-alerts"
MODEL_PATH = "models/iforest_pipeline.joblib"   # pipeline saved by train script
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "fraud_system"
COLLECTION_NAME = "flagged_transactions"

# Threshold: decision_function value below which we call anomaly.
# Based on your validation output, start near 0.01 (tune as needed).
ANOMALY_THRESHOLD = 0.01
# ----------------------------

if not os.path.exists(MODEL_PATH):
    raise SystemExit(f"Model pipeline not found at {MODEL_PATH}. Run train_isolation_forest.py first.")

print("Loading model pipeline:", MODEL_PATH)
model = joblib.load(MODEL_PATH)   # pipeline: scaler + iforest
print("Model pipeline loaded.")

# Kafka producer (used to send alerts)
producer = KafkaProducer(
    bootstrap_servers=[BOOTSTRAP],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Mongo client
mongo = MongoClient(MONGO_URI)
collection = mongo[DB_NAME][COLLECTION_NAME]

def extract_features_dict(tx: dict):
    """
    Convert incoming transaction dict to a features dict with keys:
    'amount', 'hour', 'loc' (matching training columns).
    """
    amount = float(tx.get("amount", 0.0))
    t = tx.get("time")
    hour = 0
    if t:
        try:
            # handle ISO timestamps with/without Z
            hour = datetime.fromisoformat(t.replace("Z", "+00:00")).hour
        except Exception:
            try:
                hour = int(tx.get("hour", 0) or 0)
            except:
                hour = 0
    loc_raw = str(tx.get("location", "") or "")
    digits = "".join([c for c in loc_raw if c.isdigit()])
    if digits:
        loc = int(digits) % 100
    else:
        loc = sum(ord(c) for c in loc_raw) % 100
    return {"amount": amount, "hour": int(hour), "loc": int(loc)}

def handle_transaction(tx: dict):
    feat = extract_features_dict(tx)
    # build DataFrame with exact column order/names used during training
    X = pd.DataFrame([feat], columns=["amount","hour","loc"])

    # decision_function: higher => more normal, lower => more anomalous
    score = float(model.decision_function(X)[0])
    # optional: also get hard predict if useful
    # pred = int(model.predict(X)[0])   # 1 normal, -1 anomaly

    if score < ANOMALY_THRESHOLD:
        alert = {
            "transaction_id": tx.get("transaction_id"),
            "user_id": tx.get("user_id"),
            "amount": tx.get("amount"),
            "time": tx.get("time"),
            "ml_score": score,
            "alert": "ML_SUSPICIOUS_TRANSACTION"
        }
        # save to mongo
        try:
            collection.insert_one({**alert, "raw_transaction": tx, "_created_at": datetime.utcnow().isoformat()})
        except Exception as e:
            print("Mongo insert error:", e)

        # produce to kafka
        try:
            producer.send(TOPIC_OUT, value=alert)
            producer.flush()
        except Exception as e:
            print("Kafka produce error:", e)

        print("⚠️  ML flagged transaction:", alert)
    else:
        print("OK:", {"transaction_id": tx.get("transaction_id"), "amount": tx.get("amount"), "score": score})

def create_consumer():
    return KafkaConsumer(
        TOPIC_IN,
        bootstrap_servers=[BOOTSTRAP],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id="fraud-ml-consumer",
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        # no consumer_timeout_ms so this consumer runs indefinitely
    )

def main_loop():
    while True:
        consumer = None
        try:
            consumer = create_consumer()
            print("ML consumer connected, listening for transactions...")
            for msg in consumer:
                try:
                    tx = msg.value
                    handle_transaction(tx)
                except Exception as e:
                    print("Error handling transaction:", e)
                    traceback.print_exc()
        except errors.NoBrokersAvailable:
            print("No Kafka brokers available. Retrying in 5s...")
            time.sleep(5)
            continue
        except Exception as e:
            print("Consumer error, restarting in 5s:", e)
            traceback.print_exc()
            time.sleep(5)
            continue
        finally:
            try:
                if consumer:
                    consumer.close()
            except:
                pass
            time.sleep(1)

if __name__ == "__main__":
    try:
        print(f"Using ANOMALY_THRESHOLD = {ANOMALY_THRESHOLD}")
        main_loop()
    except KeyboardInterrupt:
        print("Shutting down (KeyboardInterrupt).")
    finally:
        try:
            producer.close()
        except:
            pass
        try:
            mongo.close()
        except:
            pass
        print("Consumer stopped.")
