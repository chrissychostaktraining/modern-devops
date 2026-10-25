#!/usr/bin/env python3
"""Ch 1: AWS CDK v2 Multi-Stack KMS + SQS Blueprint."""
import os
from dataclasses import dataclass


@dataclass
class CdkStackSynthesizer:
    account: str
    region: str
    encrypted: bool = True

    def synth_manifest(self) -> dict:
        return {
            "app": "ModernDevOpsCdkV2",
            "env": {
                "account": self.account,
                "region": self.region,
            },
            "stacks": [
                {
                    "id": "KeyStack",
                    "resource": "AWS::KMS::Key",
                    "rotation": True,
                },
                {
                    "id": "QueueStack",
                    "resource": "AWS::SQS::Queue",
                    "kms_encrypted": self.encrypted,
                },
            ],
        }


if __name__ == "__main__":
    region = os.getenv("REGION", "us-east-1")
    synth = CdkStackSynthesizer("123456789012", region)
    print(synth.synth_manifest())
