# geo-track
GeoTrack is a geo-distributed parcel tracking and estimated-time-of-arrival (ETA) platform designed to simulate real-world logistics data across multiple regions. It showcases partitioning, replication, fault tolerance, and observability in a distributed database system using CockroachDB and Kafka as core components.

# Overview
GeoTrack models a multi-region parcel logistics network, demonstrating how distributed systems handle massive event streams, regional data locality, and real-time updates.
It includes synthetic data generation of millions of parcel events, Kafka-based ingestion, CockroachDB geo-partitioned storage, and metrics visualization with Prometheus & Grafana.

# Observability
- Prometheus: scrapes metrics from API and Kafka consumer.
- Grafana Dashboards:
    - API latency (p50, p90, p99)
    - DB write/read throughput
    - Kafka consumer lag
    - Node availability

# 🧨 Fault Tolerance Testing
- Chaos Tests:
    - Node failure (kill CockroachDB node)
    - Zone network partition
    - Broker crash & recovery
- Metrics Captured:
    - Read/write latency during failures
    - Replication lag
    - Recovery time post-failover

# 🧰 Setup & Deployment
- Prerequisites
- Docker & Docker Compose
- Python 3.9+
- Kafka & CockroachDB images
- Prometheus & Grafana