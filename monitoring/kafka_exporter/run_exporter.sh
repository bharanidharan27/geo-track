#!/bin/bash
export $(grep -v '^#' ../../.env | xargs)
./kafka_exporter \
  --web.listen-address=":9308" \
  --kafka.server="$KAFKA_BOOTSTRAP_SERVERS" \
  --sasl.enabled \
  --sasl.username="$KAFKA_USER" \
  --sasl.password="$KAFKA_PASSWORD" \
  --sasl.mechanism="scram-sha256" \
  --tls.enabled 

