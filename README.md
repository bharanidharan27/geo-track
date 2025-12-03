# GeoTrack – README

## 1. Install Python Dependencies

First install all Python dependencies:

    pip3 install -r requirements.txt

## 2. Synthetic Data Generation

Run the synthetic data generator:

    python3 generator/generator.py

## 3. Kafka Consumer Services

### 3.1 Start Regional Consumers

For each region, the index is:

- 0
- 1
- 2
- 3
- 4

Start one consumer instance per region in separate terminals:

    python3 -m ingestion_service.kafka_consumer 0
    python3 -m ingestion_service.kafka_consumer 1
    python3 -m ingestion_service.kafka_consumer 2
    python3 -m ingestion_service.kafka_consumer 3
    python3 -m ingestion_service.kafka_consumer 4

### 3.2 Start DLQ Consumer

Start the DLQ consumer:

    python3 -m ingestion_service.kafka_dlq_consumer

### 3.3 Scaling Consumers

To spin up more consumer instances, open new terminals and run the same commands again for the required region indices.

## 4. Prometheus and Grafana
    ./prometheus --config.file=../prometheus.yml
    
    brew services start grafana

## 5. Running the UI

### 5.1 Backend (FastAPI)

From the project root:

    cd backend
    python3 -m uvicorn main:app --reload

### 5.2 Frontend (React)

From the project root:

    cd frontend
    npm i
    npm start
