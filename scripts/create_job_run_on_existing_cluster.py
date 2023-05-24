import uuid

from databricks.databricks_service import DatabricksService, SecretsConfig


def create_job_run_on_existing_cluster():
    secret_config: SecretsConfig = SecretsConfig(_env_file="../.env")
    databricks_service: DatabricksService = DatabricksService(secret_config)
    job_id: str = str(uuid.uuid4())
    package_name: str = "dbscripts"
    entry_point: str = "dbscript1"
    databricks_service.create_job_run_on_existing_cluster(
        job_id=job_id,
        cluster_id="0526-075230-y2faqp51",
        package_name=package_name,
        entry_point=entry_point,
        positional_arguments=["An argument in an existing cluster"],
    )


if __name__ == "__main__":
    create_job_run_on_existing_cluster()
