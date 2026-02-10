# fog/fog_spark_streaming.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, avg, count
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, ArrayType
import config
import json

class FogSparkStreaming:
    """
    Fog layer using Spark Streaming for real-time aggregation
    
    This is more scalable than the simple Kafka consumer
    """
    
    def __init__(self):
        self.spark = None
        self.init_spark()
    
    def init_spark(self):
        """Initialize Spark session"""
        try:
            self.spark = SparkSession.builder \
                .appName("FogLayerStreaming") \
                .master("local[*]") \
                .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1") \
                .config("spark.sql.streaming.checkpointLocation", "./checkpoints") \
                .getOrCreate()
            
            self.spark.sparkContext.setLogLevel("WARN")
            
            print("✓ Spark Session initialized")
            return True
            
        except Exception as e:
            print(f"✗ Spark initialization failed: {e}")
            print("\nNote: Spark Streaming requires additional setup.")
            print("For simple testing, use fog_kafka_aggregator.py instead.")
            return False
    
    def define_schema(self):
        """
        Define schema for incoming Edge weights
        """
        weights_schema = StructType([
            StructField("intersection_id", IntegerType(), True),
            StructField("model_type", StringType(), True),
            StructField("feature_importances", ArrayType(DoubleType()), True),
            StructField("accuracy", DoubleType(), True)
        ])
        
        schema = StructType([
            StructField("intersection_id", IntegerType(), True),
            StructField("timestamp", StringType(), True),
            StructField("weights", weights_schema, True),
            StructField("message_type", StringType(), True)
        ])
        
        return schema
    
    def stream_from_kafka(self):
        """
        Read streaming data from Kafka
        """
        if not self.spark:
            return None
        
        schema = self.define_schema()
        
        # Read from Kafka
        df = self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", config.KAFKA_BOOTSTRAP_SERVERS[0]) \
            .option("subscribe", config.KAFKA_TOPIC_EDGE_TO_FOG) \
            .option("startingOffsets", "latest") \
            .load()
        
        # Parse JSON
        parsed_df = df.select(
            from_json(col("value").cast("string"), schema).alias("data")
        ).select("data.*")
        
        return parsed_df
    
    def aggregate_by_region(self, df):
        """
        Aggregate weights by region using Spark
        """
        # This is a simplified example
        # In production, you'd implement proper FedAvg here
        
        aggregated = df.groupBy("intersection_id") \
            .agg(
                count("*").alias("count"),
                avg("weights.accuracy").alias("avg_accuracy")
            )
        
        return aggregated
    
    def start_streaming(self):
        """
        Start the streaming pipeline
        """
        print("\n" + "="*70)
        print("SPARK STREAMING FOG LAYER")
        print("="*70)
        
        # Read stream
        stream_df = self.stream_from_kafka()
        
        if stream_df is None:
            return
        
        # Aggregate
        aggregated_df = self.aggregate_by_region(stream_df)
        
        # Write to console (for testing)
        # In production, you'd write to Kafka (fog-to-cloud topic)
        query = aggregated_df \
            .writeStream \
            .outputMode("update") \
            .format("console") \
            .option("truncate", "false") \
            .start()
        
        print("\nStreaming started...")
        print("Waiting for data from Edge nodes...\n")
        
        query.awaitTermination()
    
    def stop(self):
        """Stop Spark session"""
        if self.spark:
            self.spark.stop()
            print("✓ Spark session stopped")


def main():
    """
    Run Spark Streaming Fog layer
    """
    print("="*70)
    print("INITIALIZING SPARK STREAMING FOG LAYER")
    print("="*70)
    print("\nNote: This requires Spark with Kafka integration.")
    print("For simpler testing, use: python fog/fog_kafka_aggregator.py\n")
    
    fog_spark = FogSparkStreaming()
    
    if fog_spark.spark:
        try:
            fog_spark.start_streaming()
        except KeyboardInterrupt:
            print("\nStopped by user")
        finally:
            fog_spark.stop()
    else:
        print("\nSpark not available. Using standard Kafka aggregator instead...")
        print("Run: python fog/fog_kafka_aggregator.py")


if __name__ == "__main__":
    main()