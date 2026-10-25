#!/usr/bin/env python3
"""Ch 2: AWS SDK (Boto3) Resilient SQS Message Handler."""
import json
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class SqsMessage:
    message_id: str
    body: str
    attributes: Dict[str, str]


def process_sqs_batch(
    messages: List[SqsMessage],
) -> Dict[str, List[str]]:
    succeeded: List[str] = []
    failed: List[str] = []
    for msg in messages:
        try:
            payload = json.loads(msg.body)
            if "order_id" not in payload:
                raise ValueError("Missing order_id")
            succeeded.append(msg.message_id)
        except Exception:
            failed.append(msg.message_id)
    return {
        "processed": succeeded,
        "batchItemFailures": failed,
    }


if __name__ == "__main__":
    batch = [
        SqsMessage(
            "msg-01",
            '{"order_id": "ORD-100"}',
            {"AWSTraceHeader": "Root=1-6789"},
        )
    ]
    print(process_sqs_batch(batch))
