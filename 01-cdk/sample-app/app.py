#!/usr/bin/env python3
import os

import aws_cdk as cdk

from queue.queue_stack import QueueStack
from key.key_stack import KeyStack
from application.app_stack import AppStack

the_region = os.getenv("REGION", "us-east-1")
the_acc = os.getenv("ACCOUNT", "")
task_account = int(os.getenv("TASK_DESIRED_COUNT", 0))

env = cdk.Environment(account=the_acc, region=the_region)

app = cdk.App()

# Place my stacks
key_stack = KeyStack(app, "KeyStack") # key_stack.encryption_key
queue_stack = QueueStack(app, "QueueStack", key=key_stack.encryption_key)
app_stack = AppStack(app, "AppStackEu", task_count=task_account, env=env)

app.synth()
