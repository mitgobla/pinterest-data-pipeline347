# Databricks notebook source
# MAGIC %md
# MAGIC # Imports and Common Functions
# MAGIC
# MAGIC Imports that are used across all notebooks. Functions that may get used across multiple notebooks.

# COMMAND ----------

import pyspark.sql.dataframe as dataframe
import pyspark.sql.functions as Funcs
import pyspark.sql.types as Types
USER_ID = dbutils.widgets.get("USER_ID")
MOUNT = f"s3a://user-{USER_ID}-bucket"

AWS_KEYS_DF = spark.read.format("delta").load("dbfs:/user/hive/warehouse/authentication_credentials")
ACCESS_KEY = AWS_KEYS_DF.select('Access key ID').collect()[0]['Access key ID']
SECRET_KEY = AWS_KEYS_DF.select('Secret access key').collect()[0]['Secret access key']

# COMMAND ----------

# MAGIC %md
# MAGIC Function to create a dataframe from a topic.

# COMMAND ----------

def create_topic_dataframe(topic_name) -> dataframe.DataFrame:
    topic_dir = f"{MOUNT}/topics/{USER_ID}.{topic_name}/partition=0/*.json"
    return spark.read.format("json") \
    .option("inferSchema", "true") \
    .load(topic_dir)

# COMMAND ----------

# MAGIC %md
# MAGIC Function to create a dataframe from a Kinesis stream

# COMMAND ----------

def create_stream_dataframe(stream_name):
    return spark.readStream \
        .format('kinesis') \
        .option('streamName', stream_name) \
        .option('region', 'us-east-1') \
        .option('initialPosition', 'earliest') \
        .option('awsAccessKey', ACCESS_KEY) \
        .option('awsSecretKey', SECRET_KEY) \
        .load()
