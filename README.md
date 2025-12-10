# 🚨 Event-Driven Fraud Detection System

### Real-Time Streaming | Kafka | Python | Machine Learning (Pretrained Model) | MongoDB | Docker

This project implements a real-time **fraud detection pipeline** using an event-driven architecture.  
Bank transactions are streamed through **Apache Kafka**, scored in real time using a **pretrained ML anomaly detection model**, and suspicious events trigger downstream alerts and database logging.

The goal of this project is to demonstrate **Kafka-based streaming**, **Python consumers/producers**, **real-time fraud scoring**, and **microservice-style design**.  
ML training is _not_ part of the runtime — the system loads a **pretrained Isolation Forest model**.

---

## ✨ Features

### ✔ Event-Driven Microservices

- Kafka producers simulate transactions
- Multiple consumers process and route events
- Decoupled, scalable real-time services

### ✔ Real-Time ML Fraud Detection

- Uses a **pretrained Isolation Forest model** (`models/iforest_pipeline.joblib`)
- Scores transactions in real time
- Identifies anomalies based on ML decision scores

### ✔ Multi-Service Streaming Pipeline

- **Transaction Producer** generates live transaction events
- **Fraud Detection Consumer** loads pretrained model & scores events
- **Notification Consumer** sends/prints fraud alerts
- **MongoDB** stores flagged transactions for auditing

### ✔ Dockerized Infrastructure

- Kafka
- Zookeeper
- MongoDB  
  All managed via `docker-compose`.

---

## 📂 Project Structure

EVENT DRIVEN FAULT DETECTION
│
├── configs/
│ ├── consumer.properties
│ ├── producer.properties
│ └── server.properties
│
├── consumers/
│ ├── fraud_detection_consumer_ml.py
│ ├── fraud_detection_consumer.py
│ └── notification_consumer.py
│
├── models/
│ ├── iforest_pipeline.joblib
│ └── iforest.joblib
│
├── notebooks/
│ ├── isolation_forest.py
│ └── kafka_fraud_detection.py
│
├── producers/
│ ├── transaction_producer.py
│ └── user_profile_producer.py
│
├── resources/
│ └── kafka_best_practices.md
│
├── schema_registry/
│ ├── register_schema.sh
│ └── transaction_schema.avsc
│
├── stream_processing/
│ ├── kafka_stream_processing.py
│ └── ksql_queries.sql
│
├── docker-compose.yml
└── README.md

---

## Summary

This project delivers an end-to-end real-time fraud detection system built with:

- Apache Kafka
- Python microservices
- Pretrained ML model (Isolation Forest)
- MongoDB
- Docker

It showcases event-driven architecture, scalable stream processing, and practical ML integration in production-style workflows.
