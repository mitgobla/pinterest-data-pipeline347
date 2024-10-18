from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.databricks.operators.databricks import DatabricksSubmitRunOperator

USER_ID = "my_aws_user_id"
CLUSTER_ID = "my_databricks_cluster_id"
INTERVAL = "@daily"
START_DATE = datetime(2024, 10, 17)
RETRIES = 3

NOTEBOOK_PARAMS = {
    "notebook_path": "/Workspace/Users/my-name@my-email.com/pinterest-data-pipeline347/databricks/5. Querying Data",
    "base_parameters": {
        "USER_ID": USER_ID
    }
}

TASK_PARAMS = {
    "notebook_task": NOTEBOOK_PARAMS,
    "existing_cluster_id": CLUSTER_ID,
    "databricks_conn_id": "databricks_default"
}

DAG_ARGS = {
    'owner': USER_ID,
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': RETRIES,
    'retry_delay': timedelta(minutes=2)
}

with DAG(
    dag_id=f"{USER_ID}_dag",
    schedule_interval=INTERVAL,
    start_date=START_DATE,
    catchup=False,
    default_args=DAG_ARGS
    ) as dag:

    notebook_run = DatabricksSubmitRunOperator(
        task_id='submit_run',
        json=TASK_PARAMS
    )

    notebook_run