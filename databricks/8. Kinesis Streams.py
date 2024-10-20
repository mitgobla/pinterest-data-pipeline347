# Databricks notebook source
# MAGIC %md
# MAGIC # Processing data from Kinesis Streams

# COMMAND ----------

# MAGIC %run "./1. Imports and Common Functions"

# COMMAND ----------

# MAGIC %run "./7. Transformation Functions"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Define Schema for JSON data payload

# COMMAND ----------

pin_schema = Types.StructType([
  Types.StructField("index", Types.LongType()),
  Types.StructField("unique_id", Types.StringType()),
  Types.StructField("title", Types.StringType()),
  Types.StructField("description", Types.StringType()),
  Types.StructField("poster_name", Types.StringType()),
  Types.StructField("follower_count", Types.StringType()),
  Types.StructField("tag_list", Types.StringType()),
  Types.StructField("image_src", Types.StringType()),
  Types.StructField("is_image_or_video", Types.StringType()),
  Types.StructField("downloaded", Types.LongType()),
  Types.StructField("save_location", Types.StringType()),
  Types.StructField("category", Types.StringType()),
])

geo_schema = Types.StructType([
    Types.StructField("country", Types.StringType()),
    Types.StructField("ind", Types.LongType()),
    Types.StructField("latitude", Types.DoubleType()),
    Types.StructField("longitude", Types.DoubleType()),
    Types.StructField("timestamp", Types.StringType()),
])

user_schema = Types.StructType([
    Types.StructField("age", Types.IntegerType()),
    Types.StructField("date_joined", Types.StringType()),
    Types.StructField("first_name", Types.StringType()),
    Types.StructField("ind", Types.LongType()),
    Types.StructField("last_name", Types.StringType()),
])

# COMMAND ----------

# MAGIC %md
# MAGIC ## Define parameters for each stream
# MAGIC
# MAGIC A stream has a name (configured on AWS Kinesis Streams), a schema to parse the JSON payload, and a function that transforms the parsed data.
# MAGIC

# COMMAND ----------

streams = {
    "pin": {
        "name": f"streaming-{USER_ID}-pin",
        "schema": pin_schema,
        "transform_func": transformations_pin,
    },
    "geo": {
        "name": f"streaming-{USER_ID}-geo",
        "schema": geo_schema,
        "transform_func": transformations_geo,
    },
    "user": {
        "name": f"streaming-{USER_ID}-user",
        "schema": user_schema,
        "transform_func": transformations_user,
    }
}

# COMMAND ----------

# MAGIC %md
# MAGIC ## Process each stream
# MAGIC
# MAGIC 1. Create a Spark Stream DataFrame.
# MAGIC 2. Extract the JSON from the `data` column.
# MAGIC 3. Parse the JSON to its own DataFrame.
# MAGIC 4. Run the transformation function on the DataFrame.
# MAGIC 5. Write the stream to a Delta table.

# COMMAND ----------

for stream_name, stream_config in streams.items():
    df = create_stream_dataframe(stream_config["name"])
    df = df.selectExpr("CAST (data AS STRING)")
    df = df.withColumn("data", Funcs.from_json(Funcs.col("data"), stream_config["schema"])).selectExpr("data.*")
    df = stream_config["transform_func"](df)
    df.writeStream.format("delta") \
        .outputMode("append") \
        .option("checkpointLocation", f"/tmp/kinesis/_checkpoints/{stream_name}/") \
        .table(f"{USER_ID}_{stream_name}_table")
