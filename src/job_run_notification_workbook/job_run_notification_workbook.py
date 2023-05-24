#!/usr/bin/env python3
import json
import re
import sys
from enum import Enum
from typing import List

import requests


class DatabricksJobRunStatus(str, Enum):
    on_start: str = "jobs.on_start"
    on_success: str = "jobs.on_success"
    on_failure: str = "jobs.on_failure"


adaptive_card_failed: dict = {
    "type": "AdaptiveCard",
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.5",
    "body": [
        {
            "type": "Container",
            "items": [
                {
                    "type": "TextBlock",
                    "text": "Failed",
                    "wrap": True,
                    "horizontalAlignment": "Center",
                    "color": "Attention",
                    "size": "ExtraLarge",
                    "weight": "Default",
                },
                {
                    "type": "FactSet",
                    "wrap": True,
                    "facts": [
                        {"title": "run_id", "value": "{{run_id}}"},
                        {"title": "request_id", "value": "{{request_id}}"},
                        {"title": "databricks_url", "value": "{{databricks_url}}"},
                        {"title": "request_payload", "value": "{{request_payload}}"},
                    ],
                },
            ],
            "style": "attention",
        }
    ],
}

adaptive_card_success: dict = {
    "type": "AdaptiveCard",
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.5",
    "body": [
        {
            "type": "Container",
            "items": [
                {
                    "type": "TextBlock",
                    "text": "Succeeded",
                    "wrap": True,
                    "horizontalAlignment": "Center",
                    "color": "Good",
                    "size": "ExtraLarge",
                    "weight": "Default",
                },
                {
                    "type": "FactSet",
                    "wrap": True,
                    "facts": [
                        {"title": "run_id", "value": "{{run_id}}"},
                        {"title": "request_id", "value": "{{request_id}}"},
                        {"title": "databricks_url", "value": "{{databricks_url}}"},
                        {"title": "request_payload", "value": "{{request_payload}}"},
                    ],
                },
            ],
            "style": "good",
        }
    ],
}

WEBHOOK_URL: str = "{webhook_url}"  # type: ignore # noqa: E501
DATABRICKS_URL: str = "{databricks_url}"
STORAGE_CONTAINER: str = "{storage_container}"


if __name__ == "__main__":
    # get the input variables
    input_variables: str = sys.argv[1]
    print(input_variables)

    # parse the request body
    request_body: List[str] = re.findall(
        r"RequestBody:(.*),RequestHeader", input_variables
    )

    if request_body:
        payload: dict = json.loads(request_body[0])

        status: str = payload["event_type"]
        run_id: int = payload["run"]["run_id"]
        run_name: str = payload["job"]["name"]
        databricks_url: str = DATABRICKS_URL
        request_payload: str = f"{STORAGE_CONTAINER}/{run_id}"

        adaptive_card: dict = (
            adaptive_card_failed
            if status == DatabricksJobRunStatus.on_failure.value
            else adaptive_card_success
        )

        # update the adaptive card with the run_id, databricks_url, and request_payload
        adaptive_card["body"][0]["items"][1]["facts"][0]["value"] = run_id
        adaptive_card["body"][0]["items"][1]["facts"][1]["value"] = run_name
        adaptive_card["body"][0]["items"][1]["facts"][2]["value"] = databricks_url
        adaptive_card["body"][0]["items"][1]["facts"][3]["value"] = request_payload

        requests.post(
            url=WEBHOOK_URL,
            json={
                "type": "message",
                "attachments": [
                    {
                        "contentType": "application/vnd.microsoft.card.adaptive",
                        "contentUrl": None,
                        "content": adaptive_card,
                    }
                ],
            },
        )
    else:
        raise RuntimeError(
            "Could not find or parse the 'RequestBody' information"
            "within the input variables!"
        )
