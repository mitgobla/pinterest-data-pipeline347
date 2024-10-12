# Databricks notebook source
USER_ID = dbutils.widgets.get("USER_ID")
MOUNT = f"s3a://user-{USER_ID}-bucket"

POSTS_DIR = f"{MOUNT}/topics/{USER_ID}.pin/partition=0/*.json"
GEO_DIR = f"{MOUNT}/topics/{USER_ID}.geo/partition=0/*.json"
USER_DIR = f"{MOUNT}/topics/{USER_ID}.user/partition=0/*.json"

# COMMAND ----------

import pyspark

def create_topic_dataframe(topic_dir) -> pyspark.sql.dataframe.DataFrame:
    return spark.read.format("json") \
    .option("inferSchema", "true") \
    .load(topic_dir)

# COMMAND ----------

# Create a DataFrame for the Posts topic
df_pin = create_topic_dataframe(POSTS_DIR)
df_geo = create_topic_dataframe(GEO_DIR)
df_user = create_topic_dataframe(USER_DIR)

display(geos_df)
