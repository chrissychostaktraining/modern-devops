from aws_cdk import (
    Duration,
    Stack,
    aws_sqs as sqs,
    aws_kms as kms
)
from constructs import Construct

class KeyStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.encryption_key = kms.Key(self, "Key",
            enable_key_rotation=True
        )
