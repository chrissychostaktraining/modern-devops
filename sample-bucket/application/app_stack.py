from aws_cdk import (
    Duration,
    Stack,
    CfnParameter,
    aws_sqs as sqs,
    aws_kms as kms,
    aws_ecs as ecs,
    aws_ecs_patterns as ecsp
)
from constructs import Construct

class AppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, task_count: int, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        task_memory_limit = CfnParameter(self, "TaskMemoryLimit", type="Number",
            description="The task memory limit")

        load_balanced_fargate_service = ecsp.ApplicationLoadBalancedFargateService(self, "Service",
            memory_limit_mib=task_memory_limit.value_as_number,
            desired_count=task_count,
            cpu=512,
            task_image_options=ecsp.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_registry("httpd")
            )
        )