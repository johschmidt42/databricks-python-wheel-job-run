import json
import subprocess
import uuid

input_string: str = "{WebhookName:WebHookDatabricks,RequestBody:{{data}},RequestHeader:{Connection:Keep-Alive,Accept-Encoding:gzip,Host:16770949-ee56-4141-a41b-6eabbb5d8f03.webhook.we.azure-automation.net,User-Agent:Apache-HttpClient/4.5.13,x-ms-request-id:7a5696b0-4201-413a-bca9-f44188bad2fd}}"  # type: ignore # noqa: E501

data: dict = {
    "event_type": "jobs.on_success",
    "workspace_id": str(uuid.uuid4()),
    "run": {"run_id": str(uuid.uuid4())},
    "job": {
        "job_id": str(uuid.uuid4()),
        "name": "f6b252af-45af-48f9-99fa-f5813085080f",
    },
}

input_string = input_string.replace("{{data}}", json.dumps(data))

if __name__ == "__main__":
    subprocess.run(
        [
            "python",
            "../src/job_run_notification_workbook/job_run_notification_workbook.py",
            str(input_string),
        ]
    )
