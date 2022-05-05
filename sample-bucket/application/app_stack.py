from aws_cdk import (
    Duration,
    Stack,
    aws_sqs as sqs,
    aws_kms as kms,
    aws_ecs as ecs,
    aws_ecs_patterns as ecsp
)
from constructs import Construct

class AppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        load_balanced_fargate_service = ecsp.ApplicationLoadBalancedFargateService(self, "Service",
            memory_limit_mib=1024,
            desired_count=1,
            cpu=512,
            task_image_options=ecsp.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_registry("httpd")
            )
        )