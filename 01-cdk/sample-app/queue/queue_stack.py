from aws_cdk import (
    Duration,
    Stack,
    aws_sqs as sqs,
    aws_kms as kms
)
from constructs import Construct

class QueueStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, key: kms.IKey, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        queue = sqs.Queue(
            self, "SampleBucketQueue",
            visibility_timeout=Duration.seconds(300),
            encryption_master_key=key
        )
