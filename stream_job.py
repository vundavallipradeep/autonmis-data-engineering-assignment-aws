from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, current_date
from pyspark.sql.types import StructType, StringType, IntegerType, StructField

# Define Kafka event schema
schema = StructType([
    StructField("event_id", StringType(), True),
    StructField("user_id", StringType(), True),
    StructField("event_type", StringType(), True),
    StructField("timestamp", StringType(), True),
    StructField("metadata", StructType([
        StructField("product_id", StringType(), True),
        StructField("price", IntegerType(), True),
        StructField("category", StringType(), True)
    ]), True)
])

# ✅ Initialize Spark session once
spark = SparkSession.builder \
    .appName("KafkaCassandraS3Pipeline") \
    .config("spark.cassandra.connection.host", "172.31.94.106") \
    .getOrCreate()

# Read from Kafka
df_kafka = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "172.31.93.73:9092") \
    .option("subscribe", "raw-events") \
    .load()

# Extract and parse JSON from Kafka messages
df_parsed = df_kafka.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select(
        col("data.event_id"),
        col("data.user_id"),
        col("data.event_type"),
        col("data.timestamp"),
        col("data.metadata.product_id").alias("product_id"),
        col("data.metadata.price").alias("price"),
        col("data.metadata.category").alias("category")
    )

# Read user metadata from Cassandra
df_users = spark.read \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="user_metadata", keyspace="user_keyspace") \
    .load()

# Enrich event data with user metadata
df_enriched = df_parsed.join(df_users, on="user_id", how="left") \
    .withColumn("event_date", current_date())

# Write enriched data to S3 in JSON format, partitioned by event_date
df_enriched.writeStream \
    .format("json") \
    .option("checkpointLocation", "s3a://autonmis-data-engineer/checkpoints/") \
    .option("path", "s3a://autonmis-data-engineer/events/") \
    .partitionBy("event_date") \
    .outputMode("append") \
    .start() \
    .awaitTermination()
