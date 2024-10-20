# Databricks notebook source
# MAGIC %md
# MAGIC # Querying the Data
# MAGIC
# MAGIC Various queries to get analytics on the data.

# COMMAND ----------

# MAGIC %run "./2. Create Dataframes"

# COMMAND ----------

# MAGIC %run "./3. Clean Pin Data"

# COMMAND ----------

# MAGIC %run "./4. Clean Geo Data"

# COMMAND ----------

# MAGIC %run "./5. Clean User Data"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Queries
# MAGIC
# MAGIC ### Find the most popular category in each country
# MAGIC

# COMMAND ----------

from pyspark.sql.window import Window

# Join Geo and Pin dataframes
joined_df = df_geo.join(df_pin, on="ind", how="inner")

# Group by country and category, and then count of category
joined_df = joined_df.groupBy("country", "category").agg(Funcs.count("category").alias("category_count"))

# For each country, order by category_count in descending order
window = Window.partitionBy("country").orderBy(Funcs.desc("category_count"))

# Run the rank function over the window
max_df = joined_df.withColumn("rank", Funcs.rank().over(window))

# Filter where the rank is 1, which indicates the highest category_count for that country.
output_df = max_df.filter(Funcs.col("rank") == 1).select("country", "category", "category_count")

display(output_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Find which was the most popular category each year

# COMMAND ----------

# Join geo and pin dataframe to get timestamp
joined_df = df_geo.join(df_pin, on="ind", how="inner")

# Extract year from timestamp
joined_df = joined_df.withColumn("post_year", Funcs.year("timestamp"))

# Group by year and category, and then count of category
joined_df = joined_df.groupBy("post_year", "category").agg(Funcs.count("category").alias("category_count"))

# For each year, order by category_count in descending order
window = Window.partitionBy("post_year").orderBy(Funcs.desc("category_count"))

# Run the rank function over the window
max_df = joined_df.withColumn("rank", Funcs.rank().over(window))

# Filter where the rank is 1, which indicates the highest category_count for that year
# Additionally filter by year to only show years between 2018 and 2022
output_df = max_df.filter(Funcs.col("rank") == 1).filter((Funcs.col("post_year") >= 2018) & (Funcs.col("post_year") <= 2022)).select("post_year", "category", "category_count")

display(output_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Find the user with most followers in each country
# MAGIC
# MAGIC 1. For each country find the user with the most followers (country, poster_name, follower_count)
# MAGIC 2. Based on the above query, find the country with the user with most followers (country, follower_count)
# MAGIC

# COMMAND ----------

joined_df = df_geo.join(df_pin, on="ind", how="inner")

# Group by country and get max of follower_count
country_df = joined_df.groupBy("country").agg(Funcs.max("follower_count").alias("max_follower_count")).alias("c_max")

# Join grouped dataframe with original dataframe, to only have rows that have matching country and max follower_count
joined_df = joined_df.join(country_df, on=(joined_df.country == country_df.country) & (joined_df.follower_count == country_df.max_follower_count), how="inner")

# Select only columns we need, sort by follower_count in descending order
joined_df = joined_df.select("c_max.country", "poster_name", "follower_count").sort("follower_count", ascending=False)

display(joined_df)

# COMMAND ----------

# Select all rows that have the max follower_count
# First collect the max follower_count value by running max on the follower_count column
# This value is then compared to for the filter
max_count = joined_df.agg(Funcs.max("follower_count").alias("max_count")).collect()[0]["max_count"]
print(max_count)
joined_df = joined_df.filter(joined_df["follower_count"] == max_count)
display(joined_df)

# COMMAND ----------

joined_df = df_user.join(df_pin, on="ind", how="inner")
display(joined_df)

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC ### Find the most popular category based on age groups
# MAGIC - 18-24
# MAGIC - 25-35
# MAGIC - 36-50
# MAGIC - 50+
# MAGIC
# MAGIC Columns `age_group` based on original `age` column, `category`, `category_count`
# MAGIC

# COMMAND ----------

joined_df = df_user.join(df_pin, on="ind", how="inner")

# Create age_group based on age values
age_group_df = joined_df.withColumn(
    "age_group",
    Funcs.when((Funcs.col("age") >= 18) & (Funcs.col("age") <= 24), "18-24")
    .when((Funcs.col("age") >= 25) & (Funcs.col("age") <= 35), "25-35")
    .when((Funcs.col("age") >= 36) & (Funcs.col("age") <= 50), "36-50")
    .when((Funcs.col("age") >= 51), "51+")
    .otherwise("Unknown")
)


joined_df = age_group_df.groupBy("age_group", "category").agg(Funcs.count("category").alias("category_count"))

window = Window.partitionBy("age_group").orderBy(Funcs.col("category_count").desc())

joined_df = joined_df.withColumn("rank", Funcs.row_number().over(window))

joined_df = joined_df.filter(joined_df["rank"] == 1).select("age_group", "category", "category_count")

display(joined_df)


# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC ### Find the median follower count for different age groups
# MAGIC

# COMMAND ----------

# pyspark.sql.functions.median is only present in pyspark >= 3.4.0, this cluster is using 3.2.1 so using percentile_approx instead

# Median follower_count for each age_group
joined_df = age_group_df.groupBy("age_group").agg(Funcs.percentile_approx("follower_count", 0.5).alias("median_follower_count"))

# Sort by median_follower_count in descending order
joined_df = joined_df.orderBy(Funcs.col("median_follower_count").desc())

display(joined_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Find how many users have joined between 2015 and 2020. 
# MAGIC
# MAGIC - `post_year` and `number_users_joined` 

# COMMAND ----------

joined_df = df_user.join(df_pin, on="ind", how="inner")

# Create column that extracts year part from join_date
joined_df = joined_df.withColumn("post_year", Funcs.year("date_joined"))

# Only get rows where year is between 2015 and 2020
joined_df = joined_df.filter((Funcs.col("post_year") >= 2015) & (Funcs.col("post_year") <= 2020))

# Group by year, and count number of users who joined in each year
joined_df = joined_df.groupBy("post_year").agg(Funcs.count("ind").alias("number_users_joined"))

# Sort by year
joined_df = joined_df.orderBy(Funcs.col("post_year"))

display(joined_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Find the median follower count of users have joined between 2015 and 2020. 

# COMMAND ----------

joined_df = df_user.join(df_pin, on="ind", how="inner")

# Create column that extracts year part from join_date
joined_df = joined_df.withColumn("post_year", Funcs.year("date_joined"))

# Only get rows where year is between 2015 and 2020
joined_df = joined_df.filter((Funcs.col("post_year") >= 2015) & (Funcs.col("post_year") <= 2020))

# Group by year, and get median (percentile_approx) of follower_count
joined_df = joined_df.groupBy("post_year").agg(Funcs.percentile_approx("follower_count", 0.5).alias("median_follower_count"))

# Sort by year
joined_df = joined_df.orderBy(Funcs.col("post_year"))

display(joined_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Find the median follower count of users that have joined between 2015 and 2020, based on which age group they are part of. 

# COMMAND ----------

# Merge since we need follower_count from df_pin
joined_df = df_user.join(df_pin, on="ind", how="inner")

# Extract year part of join date
joined_df = joined_df.withColumn("post_year", Funcs.year("date_joined"))

# Only get rows where year is between 2015 and 2020
joined_df = joined_df.filter((Funcs.col("post_year") >= 2015) & (Funcs.col("post_year") <= 2020))

# Create column with age groups
joined_df = joined_df.withColumn(
    "age_group",
    Funcs.when((Funcs.col("age") >= 18) & (Funcs.col("age") <= 24), "18-24")
    .when((Funcs.col("age") >= 25) & (Funcs.col("age") <= 35), "25-35")
    .when((Funcs.col("age") >= 36) & (Funcs.col("age") <= 50), "36-50")
    .when((Funcs.col("age") >= 51), "51+")
    .otherwise("Unknown")
)

# group by year, and then by age group, and get median follower_count
joined_df = joined_df.groupBy("post_year", "age_group").agg(Funcs.percentile_approx("follower_count", 0.5).alias("median_follower_count"))

# sort by year, then by age group
joined_df = joined_df.orderBy(Funcs.col("post_year"), Funcs.col("age_group"))

display(joined_df)
