# Databricks notebook source
# MAGIC %md
# MAGIC # Transformation Functions
# MAGIC
# MAGIC After testing and confirming all the transformations work for the dataframes during batch processing, this notebook wraps them into a single function so they can be used for stream processing.

# COMMAND ----------

# MAGIC %run "./1. Imports and Common Functions"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pin/Post Transformation

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

def transformations_pin(df_pin: dataframe.DataFrame):
  df_pin = df_pin.dropDuplicates(['unique_id'])

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
  
  # Parse follower count using user defined function
  parse_follower_count_udf = Funcs.udf(parse_follower_count, Types.IntegerType())
  df_pin = df_pin.withColumn("follower_count", parse_follower_count_udf(Funcs.col("follower_count")).cast(Types.IntegerType()))

  # Clean save_location column
  df_pin = df_pin.withColumn("save_location", Funcs.regexp_replace("save_location", "Local save in ", ""))

  # Rename index
  df_pin = df_pin.withColumnRenamed("index", "ind")

  # Reorder columns
  df_pin = df_pin.select("ind", "unique_id", "title", "description", "follower_count", "poster_name", "tag_list", "is_image_or_video", "image_src", "save_location", "category")

  return df_pin


# COMMAND ----------

# MAGIC %md
# MAGIC ## Geo Transformation

# COMMAND ----------

def transformations_geo(df_geo: dataframe.DataFrame):
  # Combine latitude and longitude into a single column, then drop the two columns  
  df_geo = df_geo.withColumn("coordinates", Funcs.array("latitude", "longitude"))
  df_geo = df_geo.drop("latitude", "longitude")

  # Cast timestamp column
  df_geo = df_geo.withColumn("timestamp", Funcs.to_timestamp("timestamp"))

  # Reorder columns
  df_geo = df_geo.select("ind", "country", "coordinates", "timestamp")
  return df_geo



# COMMAND ----------

# MAGIC %md
# MAGIC ## User Transformation

# COMMAND ----------

def transformations_user(df_user: dataframe.DataFrame):
  # Combine first_name and last_name to a single column
  df_user = df_user.withColumn("user_name", Funcs.concat("first_name", Funcs.lit(" "), "last_name"))
  df_user = df_user.drop("first_name", "last_name")

  # Cast date_joined column
  df_user = df_user.withColumn("date_joined", Funcs.to_timestamp("date_joined"))

  # Reorder columns
  df_user = df_user.select("ind", "user_name", "age", "date_joined")
  return df_user
