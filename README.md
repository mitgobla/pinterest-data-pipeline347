# Pinterest Data Pipeline

Creating a similar system to Pinterest using the AWS Cloud.

- [Pinterest Data Pipeline](#pinterest-data-pipeline)
  - [Project Description](#project-description)
  - [Project Structure](#project-structure)
  - [Setup Instructions](#setup-instructions)
  - [Usage Instructions](#usage-instructions)
    - [Sending Data to API](#sending-data-to-api)
      - [Setup Python Environment](#setup-python-environment)
      - [Emulate data sending to API:](#emulate-data-sending-to-api)
    - [Cleaning \& Analysing Data](#cleaning--analysing-data)
  - [Reflection on Project](#reflection-on-project)
    - [Amazon Web Services](#amazon-web-services)
    - [Databricks](#databricks)
    - [Airflow](#airflow)

## Project Description

This project aims to replicate an end-to-end pipeline for data processing similar to that used in Pinterest. Using AWS services like EC2, MSK, and S3, with integration into Databricks for analytics. Kafka is used for creating a system to collect streaming data, with storage in S3 and analysis in Databricks.

I have learned how to configure Kafka clusters, set up secure IAM authentication for Kafka topics, and manage S3 buckets. Additionally, I have been able to gain experience in mounting S3 buckets into Databricks. This has deepened my understanding of cloud-based data streaming and given me an opportunity to use these tools hands-on to produce a project that replicates one that is used in industry.

## Project Structure

- `databricks` contains Databricks Notebook code for data transformations and queries. Each file is explained in [Cleaning & Analysing Data](#cleaning--analysing-data)
- `airflow` contains DAG workflow for executing a Databricks Notebook.
- Apache Kafka, AWS API Gateway
  - `kafka_api.py` provides an interface for interacting with the MSK Cluster on AWS.
  - `api_conf.example.yaml` is an example configuration for the `KafkaAPI` class.
  - `user_posting_emulation.py` is used to fetch data from an RDS database, and then send the data to the MSK Cluster via `KafkaAPI`.
- AWS Kinesis, AWS API Gateway
  - `kinesis_api.py` provides an interface for interacting with the Kinesis Streams on AWS.
  - `stream_api_conf.example.yaml` is an example configuration for the `KinesisAPI` class.
  - `user_posting_emulation_streams.py` is used to fetch data from an RDS database, and then send the data to the Kinesis streams via `KinesisAPI`
- `db_creds.example.yaml` is an example configuration for connecting to the RDS instance, used in both `user_posting_emulation.py` and `user_posting_emulation_streams.py`

## Setup Instructions

Please read [SETUP](SETUP.md) to see extensive setup instructions.

## Usage Instructions

### Sending Data to API

#### Setup Python Environment

1. Ensure Python is installed with `python --version`. This project uses Python 3.12
2. Create the environment with `python -m venv .venv`
3. Activate the environment:
   1. Windows command prompt: `.venv\Scripts\activate`
   2. Windows PowerShell: `.venv\Scripts\Activate.ps1`
   3. Linux/Mac: `source .venv\bin\activate`
4. Install requirements with `pip install -r requirements.txt`

#### Emulate data sending to API:

1. Run `python user_posting_emulation.py` to begin emulating user data being sent to the Kafka REST API.

### Cleaning & Analysing Data

Using Databricks notebooks, data is extracted from the S3 bucket, then put into Spark Dataframes, for transformation. After cleaning the data, analysis can be performed with queries.

Inside the `databricks` folder:

1. **Imports and Common Functions**: PySpark imports, grabbing AWS User ID from Databricks widget, and common functions such as creating a Dataframe from a Kafka topic.
2. **Clean Pin Data**: Steps for transforming the data in the Pin/Posts Dataframe.
3. **Clean Geo Data**: Steps for transforming the data in the Geo Dataframe.
4. **Clean User Data**: Steps for transforming the data in the Users Dataframe.
5. **Querying Data**: Various queries on the cleaned data to gather insights.
6. **Mount S3 Bucket (Legacy)**: The previous way of mounting an S3 bucket to Databricks. Now, Databricks directly accesses the S3 bucket, rather than through its own filesystem.

## Reflection on Project

### Amazon Web Services

> TODO

1. Hands on with AWS console, EC2 instance
2. Steps were clear, and AWS console has not changed much from the steps
3. Accidentally tried running the wrong Confluent Kafka script, and went researching to find cause, until I realised.
4. Creating topics, and running the Kafka REST instance, was interesting to do and be able to visualise data entering the pipeline during the user_posting_emulation code running.

### Databricks

One improvement I could make to my Databricks Notebook code is finding repetitive code, and creating a function from it. However, for sake of clarity of what I was performing on each step, I kept it how it is, and these transformations or queries could need to be adjusted depending on the requirements.

While there is similarities to PySpark and Pandas for data transformations and cleaning, I did find I had to research into PySpark more to understand how to join statements together to get the results I wanted. Additionally, I discovered that the PySpark version on the Databricks cluster was running a few versions behind, so I looked up an alternative for finding the `median`, in this case `perentile_approx`.

### Airflow

Creating a DAG and uploading it was a trivial process, especially as there is extensive documentation on Airflow's website with numerous examples. In this case, my workflow is simple, just running one task, which executes a single Databricks Notebook. A future improvement could be to execute each notebook I created in the order I want, such as gathering data, cleaning data, and then lastly querying data. At the moment, the notebooks run dependencies on other noteobooks themselves.
