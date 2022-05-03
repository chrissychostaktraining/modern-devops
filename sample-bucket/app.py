#!/usr/bin/env python3
import os

import aws_cdk as cdk

from queue.queue_stack import QueueStack
from key.key_stack import KeyStack

app = cdk.App()

# Place my stacks
key_stack = KeyStack(app, "KeyStack") # key_stack.encryption_key
queue_stack = QueueStack(app, "QueueStack", key=key_stack.encryption_key)

app.synth()