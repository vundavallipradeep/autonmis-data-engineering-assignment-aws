# Autonmis Streaming Data Pipeline

## Overview
This project demonstrates a real-time streaming data pipeline built using open-source technologies and deployed on AWS. The architecture ingests product view events via Kafka, enriches them with user metadata from Cassandra using Apache Spark Structured Streaming, and stores the final enriched records on Amazon S3 in partitioned JSON format.

## Architecture

```
Kafka Producer (Local or EC2)
       |
       V
Apache Kafka (EC2 Instance)
       |
       V
Apache Spark Structured Streaming (EMR Cluster)
       |
       V
+--------------------------+
|  Apache Cassandra (EC2)  |
+--------------------------+
       |
       V
 Amazon S3 (Data Lake Sink)
```

## Components

### 1. Kafka Producer (`producer.py`)
This script simulates real-time `product_view` events:
- Sends data to the Kafka topic `raw-events`
- Uses `kafka-python`

### 2. Spark Streaming Job (`stream_job.py`)
- Reads data from Kafka
- Parses JSON events
- Joins with `user_metadata` table from Cassandra
- Writes enriched JSON to S3, partitioned by `event_date`

### 3. Cassandra Setup (EC2 Docker)
Schema for enrichment:
```sql
CREATE KEYSPACE user_keyspace WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'};

CREATE TABLE user_keyspace.user_metadata (
    user_id text PRIMARY KEY,
    name text,
    age int,
    location text
);
```

### 4. S3 Output
Partitioned output files:
```
s3a://autonmis-data-engineer/events/event_date=YYYY-MM-DD/
```

## How to Run

### Kafka (on EC2)
```bash
# Start ZooKeeper
bin/zookeeper-server-start.sh config/zookeeper.properties

# Start Kafka Broker
bin/kafka-server-start.sh config/server.properties

# Create topic (if not already present)
bin/kafka-topics.sh --create --topic raw-events --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

# Verify topicin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

### Run Spark Job (on EMR)
```bash
spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,\
              com.datastax.spark:spark-cassandra-connector_2.12:3.4.1 \
  stream_job.py
```

### Run Producer (Local or EC2)
```bash
pip install kafka-python
python producer.py
```

## Files
```
├── producer.py              # Kafka producer script
├── stream_job.py            # Spark Structured Streaming job
├── config/
│   ├── kafka-server.properties  # Kafka config (with listeners, advertised.listeners)
│   └── cassandra-schema.cql    # CQL file for table creation
├── requirements.txt         # Required Python packages
└── README.md                # Project documentation
```

## Author
Pradeep Vundavalli

## License
This project is intended for educational/demo purposes only.

