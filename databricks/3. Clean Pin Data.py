# Databricks notebook source
# MAGIC %md
# MAGIC # Cleaning Pin Dataframe
# MAGIC
# MAGIC Using PySpark to transform and clean the Dataframes generated by JSON files from S3 bucket.

# COMMAND ----------

# MAGIC %run "./1. Imports and Common Functions"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cleaning the Posts Dataframe
# MAGIC
# MAGIC Posts (or "pins") schema: 
# MAGIC - category: string
# MAGIC - description: string
# MAGIC - downloaded: int
# MAGIC - follower_count: int
# MAGIC - image_src: string (url)
# MAGIC - index: int
# MAGIC - is_image_or_video: string
# MAGIC - poster_name: string
# MAGIC - save_location: string
# MAGIC - tag_list: string
# MAGIC - title: string
# MAGIC - unique_id: string (uuid)

# COMMAND ----------

# Remove duplicate rows that contain the same unique_id
# This shouldn't happen, but with the post emulation it can sometimes pick the same row more than once over time.
df_pin = df_pin.dropDuplicates(['unique_id'])
display(df_pin)

# COMMAND ----------

# MAGIC %md
# MAGIC Set invalid values as `None`. These values are invalid if:
# MAGIC - description: `No description available Story format`
# MAGIC - follower_count: `User Info Error`
# MAGIC - image_src: `Image src error.`
# MAGIC - poster_name: `User Info Error`
# MAGIC - tag_list: `N,o, ,T,a,g,s, ,A,v,a,i,l,a,b,l,e`
# MAGIC - title: `No Title Data Available`
# MAGIC or are empty.

# COMMAND ----------

null_mapping = {
  "description": "No description available Story format",
  "follower_count": "User Info Error",
  "image_src": "Image src error.",
  "poster_name": "User Info Error",
  "tag_list": "N,o, ,T,a,g,s, ,A,v,a,i,l,a,b,l,e",
  "title": "No Title Data Available"
}

# Go through each null mapping and replace with the appropriate value
for column, null_value in null_mapping.items():
  df_pin = df_pin.withColumn(column, Funcs.when(Funcs.col(column) == null_value, None).otherwise(Funcs.col(column)))

# Additionally replace empty values with None
for column in df_pin.columns:
  df_pin = df_pin.withColumn(column, Funcs.when(Funcs.col(column) == "", None).otherwise(Funcs.col(column)))

display(df_pin)

# COMMAND ----------

# MAGIC %md
# MAGIC Transform follower count to its integer representation. 
# MAGIC For example, a value of "12k" is 12000. A value of "45M" is 45000000.

# COMMAND ----------

# User Defined Function (UDF) which takes in string and will return an int or None
def parse_follower_count(value: str):
    if value is None:
        return None
    
    value = value.lower()
    # Check if the value ends with k or m
    # k is 1000 times, m is 1000000 times
    # Otherwise return the value if its a number already.
    if value.endswith('k'):
        return int(float(value[:-1]) * 1000)
    elif value.endswith('m'):
        return int(float(value[:-1]) * 1000000)
    elif value.isdigit():
        return int(value)
    else:
        return None

parse_follower_count_udf = Funcs.udf(parse_follower_count, Types.IntegerType())

df_pin = df_pin.withColumn("follower_count", parse_follower_count_udf(Funcs.col("follower_count")).cast(Types.IntegerType()))
display(df_pin)

# COMMAND ----------

# MAGIC %md
# MAGIC Clean the `save_location` column by removing "Local save in " so it only represents a path.

# COMMAND ----------

df_pin = df_pin.withColumn("save_location", Funcs.regexp_replace("save_location", "Local save in ", ""))
display(df_pin)

# COMMAND ----------

# MAGIC %md
# MAGIC Rename `index` column to `ind`

# COMMAND ----------

df_pin = df_pin.withColumnRenamed("index", "ind")

# COMMAND ----------

# MAGIC %md
# MAGIC Reorder columns to expected order.

# COMMAND ----------

df_pin = df_pin.select("ind", "unique_id", "title", "description", "follower_count", "poster_name", "tag_list", "is_image_or_video", "image_src", "save_location", "category")
display(df_pin)
