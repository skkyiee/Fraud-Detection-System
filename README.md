# 🚨 Event-Driven Fraud Detection System

### Real-Time Streaming | Kafka | Python | Machine Learning (Pretrained Model) | MongoDB | Docker

This project implements a real-time **fraud detection pipeline** using an event-driven architecture.  
Bank transactions are streamed through **Apache Kafka**, scored in real time using a **pretrained ML anomaly detection model**, and suspicious events trigger downstream alerts and database logging.

The goal of this project is to demonstrate **Kafka-based streaming**, **Python consumers/producers**, **real-time fraud scoring**, and **microservice-style design**.  
ML training is _not_ part of the runtime — the system loads a **pretrained Isolation Forest model**.

---

## Features

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

## 🚀 How to Run the Project

Follow these steps to start the complete real-time fraud detection pipeline.

#### Start Kafka, Zookeeper, and MongoDB (Docker)

- docker-compose up -d

#### Start the ML Fraud Detection Consumer

- python consumers/fraud_detection_consumer_ml.py

#### Start the Notification Consumer

- python consumers/notification_consumer.py

#### Start the Transaction Producer

- python producers/transaction_producer.py

#### You should now see:

- Transactions being streamed
- ML consumer scoring them
- Alerts being published
- Notifications printed
- Alerts stored in MongoDB

---

## Summary

This project delivers an end-to-end real-time fraud detection system built with:

- Apache Kafka
- Python microservices
- Pretrained ML model (Isolation Forest)
- MongoDB
- Docker

It showcases event-driven architecture, scalable stream processing, and practical ML integration in production-style workflows.
