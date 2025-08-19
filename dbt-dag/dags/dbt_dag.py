from pathlib import Path
from datetime import datetime
from cosmos import DbtDag
from cosmos.config import ProjectConfig, ProfileConfig, ExecutionConfig
from cosmos.profiles import SnowflakeUserPasswordProfileMapping
import os

# Resolve path inside the Airflow container to dags/dbt/data_pipeline
DBT_DIR = str((Path(__file__).parent / "dbt" / "data_pipeline").resolve())

project_config = ProjectConfig(dbt_project_path=DBT_DIR)

profile_config = ProfileConfig(
    profile_name="default",
    target_name="dev",
    profile_mapping=SnowflakeUserPasswordProfileMapping(
        conn_id="Snowflake_conn",
        profile_args={"database": "dbt_db", "schema": "dbt_schema"},
    ),
)

execution_config = ExecutionConfig(
    dbt_executable_path=f"{os.environ.get('AIRFLOW_HOME', '/usr/local/airflow')}/dbt_venv/bin/dbt"
)

dbt_snowflake_dag = DbtDag(
    dag_id="dbt_dag",
    schedule="@daily",
    start_date=datetime(2025, 8, 17),
    catchup=False,
    project_config=project_config,      # keyword
    profile_config=profile_config,
    execution_config=execution_config,
    operator_args={"install_deps": True},
)
