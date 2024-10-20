# Databricks notebook source
# MAGIC %md
# MAGIC # Create Dataframes
# MAGIC
# MAGIC To allow modular use of the cleaning code, Dataframes are loaded separately (in this case for batch processing)

# COMMAND ----------

# MAGIC %run "./1. Imports and Common Functions"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Dataframe
# MAGIC
# MAGIC Create Dataframes from the JSON files in the S3 bucket.

# COMMAND ----------

df_pin = create_topic_dataframe("pin")
display(df_pin)

# COMMAND ----------

df_geo = create_topic_dataframe("geo")
display(df_geo)

# COMMAND ----------

df_user = create_topic_dataframe("user")
display(df_user)
