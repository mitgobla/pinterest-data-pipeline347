# Pinterest Data Pipeline

Creating a similar system to Pinterest using the AWS Cloud.

- [Pinterest Data Pipeline](#pinterest-data-pipeline)
  - [Project Description](#project-description)
  - [Setup Instructions](#setup-instructions)
  - [Usage Instructions](#usage-instructions)
    - [Setup Python Environment](#setup-python-environment)
    - [Emulate data sending to API:](#emulate-data-sending-to-api)

## Project Description

This project aims to replicate an end-to-end pipeline for data processing similar to that used in Pinterest. Using AWS services like EC2, MSK, and S3, with integration into Databricks for analytics. Kafka is used for creating a system to collect streaming data, with storage in S3 and analysis in Databricks.

I have learned how to configure Kafka clusters, set up secure IAM authentication for Kafka topics, and manage S3 buckets. Additionally, I have been able to gain experience in mounting S3 buckets into Databricks. This has deepened my understanding of cloud-based data streaming and given me an opportunity to use these tools hands-on to produce a project that replicates one that is used in industry.

## Setup Instructions

Please read [SETUP](SETUP.md) to see extensive setup instructions.

## Usage Instructions

### Setup Python Environment

1. Ensure Python is installed with `python --version`. This project uses Python 3.12
2. Create the environment with `python -m venv .venv`
3. Activate the environment:
   1. Windows command prompt: `.venv\Scripts\activate`
   2. Windows PowerShell: `.venv\Scripts\Activate.ps1`
   3. Linux/Mac: `source .venv\bin\activate`
4. Install requirements with `pip install -r requirements.txt`

### Emulate data sending to API:

1. Run `python user_posting_emulation.py` to begin emulating user data being sent to the Kafka REST API.