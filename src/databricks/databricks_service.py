import logging
from json import JSONDecodeError
from typing import Dict, List, Optional

import httpx
from httpx import Response
from pydantic import BaseSettings

logger = logging.getLogger(__name__)


class SecretsConfig(BaseSettings):
    """
    Configuration for secrets.
    """

    DATABRICKS_URL: str
    DATABRICKS_PAT: str
    CR_USERNAME: str
    CR_PASSWORD: str


class DatabricksService:
    """
    Service to interact with Databricks API.
    Allows to create and trigger a one time job run
    using an existing cluster or a new cluster with the Databricks REST API.
    """

    DATABRICKS_API_VERSION: str = "2.1"

    cluster: dict = {
        "num_workers": 0,
        "spark_version": "12.2.x-scala2.12",
        "runtime_engine": "STANDARD",
        "node_type_id": "Standard_F4",
        "driver_node_type_id": "Standard_F4",
    }

    def __init__(self, secrets_config: SecretsConfig):
        self.secrets_config: SecretsConfig = secrets_config
        self.url_post_job_run: str = f"{self.secrets_config.DATABRICKS_URL}/api/{self.DATABRICKS_API_VERSION}/jobs/runs/submit"  # type: ignore # noqa: E501

    def create_job_run_on_existing_cluster(
        self,
        job_id: str,
        cluster_id: str,
        package_name: str,
        entry_point: str,
        positional_arguments: Optional[List[str]] = None,
        named_arguments: Optional[Dict[str, str]] = None,
        notification_ids: Optional[List[str]] = None,
    ):
        """
        Create and trigger a one time job run using an existing cluster.

        Args:
            job_id: The job id of the job run
            cluster_id: The cluster id to use
            package_name: The name of the python package to use
            entry_point: The entry point of the python package to use
            positional_arguments: Positional arguments for the entry_point
            named_arguments: Named arguments for the python entry_point
            notification_ids: The notification ids to use (system notification ids)
        """
        python_wheel_task_payload: dict = {
            "package_name": package_name,
            "entry_point": entry_point,
        }

        if positional_arguments:
            python_wheel_task_payload["parameters"] = str(positional_arguments)

        if named_arguments:
            python_wheel_task_payload["parameters"] = str(named_arguments)

        task: dict = {
            "task_key": job_id,
            "python_wheel_task": python_wheel_task_payload,
            "existing_cluster_id": cluster_id,
        }

        payload: dict = {"tasks": [task], "run_name": job_id}

        if notification_ids:
            payload["webhook_notifications"] = {
                # "on_start": {"id": id for id in notification_ids},
                "on_success": {"id": id for id in notification_ids},
                "on_failure": {"id": id for id in notification_ids},
            }

        msg: str = f"Trying to create a job run. Payload: {payload}"
        logger.info(msg)

        headers: dict = {
            "Authorization": f"Bearer {self.secrets_config.DATABRICKS_PAT}"
        }

        response: Response = httpx.post(
            url=self.url_post_job_run, headers=headers, json=payload
        )

        try:
            data: dict = response.json()
        except JSONDecodeError:
            data: dict = {"detail": response.text}

        if response.status_code == 200:
            return data
        else:
            msg: str = (
                f"Could not create a job run: {data} "
                f"URL: {self.url_post_job_run} "
                f"HTTP Status Code: {response.status_code}"
            )
            logger.error(msg)
            raise ValueError(msg)

    def create_job_run_on_new_cluster(
        self,
        job_id: str,
        image_url: str,
        package_name: str,
        entry_point: str,
        positional_arguments: Optional[List[str]] = None,
        named_arguments: Optional[Dict[str, str]] = None,
        notification_ids: Optional[List[str]] = None,
        env_vars: Optional[dict] = None,
        cluster_kwargs: Optional[dict] = None,
    ) -> dict:
        """
        Create and trigger a one time job run using a new cluster.

        Args:
            job_id: The job id of the job run
            image_url: The docker image url to use
            package_name: The name of the python package to use
            entry_point: The entry point of the python package to use
            positional_arguments: Positional arguments for the entry_point
            named_arguments: Named arguments for the python entry_point
            notification_ids: The notification ids to use (system notification ids)
            env_vars: Environment variables for new cluster (flat dict!)
            cluster_kwargs: Cluster spark settings for a new cluster
        """

        python_wheel_task_payload: dict = {
            "package_name": package_name,
            "entry_point": entry_point,
        }

        if positional_arguments:
            python_wheel_task_payload["parameters"] = str(positional_arguments)

        if named_arguments:
            python_wheel_task_payload["parameters"] = str(named_arguments)

        cluster: dict = cluster_kwargs if cluster_kwargs else self.cluster

        # tags
        cluster["custom_tags"] = {"ResourceClass": "SingleNode"}

        # single node
        cluster["spark_conf"] = {"spark.databricks.cluster.profile": "singleNode"}

        if env_vars:
            cluster["spark_env_vars"] = env_vars

        cluster["docker_image"] = {
            "url": image_url,
            "basic_auth": {
                "username": self.secrets_config.CR_USERNAME,
                "password": self.secrets_config.CR_PASSWORD,
            },
        }

        task: dict = {
            "task_key": job_id,
            "python_wheel_task": python_wheel_task_payload,
            "new_cluster": cluster,
        }

        payload: dict = {"tasks": [task], "run_name": job_id}

        if notification_ids:
            payload["webhook_notifications"] = {
                # "on_start": {"id": id for id in notification_ids},
                "on_success": {"id": id for id in notification_ids},
                "on_failure": {"id": id for id in notification_ids},
            }

        msg: str = f"Trying to create a job run. Payload: {payload}"
        logger.info(msg)

        headers: dict = {
            "Authorization": f"Bearer {self.secrets_config.DATABRICKS_PAT}"
        }

        response: Response = httpx.post(
            url=self.url_post_job_run, headers=headers, json=payload
        )

        try:
            data: dict = response.json()
        except JSONDecodeError:
            data: dict = {"detail": response.text}

        if response.status_code == 200:
            return data
        else:
            msg: str = (
                f"Could not create a job run: {data} "
                f"URL: {self.url_post_job_run} "
                f"HTTP Status Code: {response.status_code}"
            )
            logger.error(msg)
            raise ValueError(msg)
