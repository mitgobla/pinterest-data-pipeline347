# Databricks notebook source
from pyspark.sql.functions import *
import urllib

# Load credentials from delta table
delta_table_path = "dbfs:/user/hive/warehouse/authentication_credentials"
aws_keys_df = spark.read.format("delta").load(delta_table_path)

# COMMAND ----------

# Get key and secret key from spark dataframe
ACCESS_KEY = aws_keys_df.select("Access key ID").collect()[0]['Access key ID']
SECRET_KEY = aws_keys_df.select("Secret access key").collect()[0]['Secret access key']

ENCODED_SECRET_KEY = urllib.parse.quote(SECRET_KEY, safe='')

# COMMAND ----------

# Mount the S3 bucket (now legacy)
S3_BUCKET = "user-#########-bucket"
MOUNT_NAME = f"/mnt/{S3_BUCKET}"
SOURCE_URL = f"s3n://{ACCESS_KEY}:{ENCODED_SECRET_KEY}@{S3_BUCKET}"

dbutils.fs.mount(SOURCE_URL, MOUNT_NAME)
