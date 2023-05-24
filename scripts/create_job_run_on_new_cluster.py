import uuid

from databricks.databricks_service import DatabricksService, SecretsConfig


def create_job_run_on_new_cluster():
    secret_config: SecretsConfig = SecretsConfig(_env_file="../.env")
    databricks_service: DatabricksService = DatabricksService(secret_config)
    job_id: str = str(uuid.uuid4())
    image_url: str = "databricksjobrunacr.azurecr.io/databricks-wheel-scripts:latest"
    package_name: str = "dbscripts"
    entry_point: str = "dbscript1"
    databricks_service.create_job_run_on_new_cluster(
        job_id=job_id,
        image_url=image_url,
        package_name=package_name,
        entry_point=entry_point,
        positional_arguments=["An argument in a new cluster"],
    )


if __name__ == "__main__":
    create_job_run_on_new_cluster()
