# Databricks notebook source
import pyspark.sql.dataframe as dataframe
import pyspark.sql.functions as Funcs
import pyspark.sql.types as Types

USER_ID = dbutils.widgets.get("USER_ID")
MOUNT = f"s3a://user-{USER_ID}-bucket"

# COMMAND ----------

def create_topic_dataframe(topic_name) -> dataframe.DataFrame:
    topic_dir = f"{MOUNT}/topics/{USER_ID}.{topic_name}/partition=0/*.json"
    return spark.read.format("json") \
    .option("inferSchema", "true") \
    .load(topic_dir)
