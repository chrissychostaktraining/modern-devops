import boto3

# Get the service resource
sqs = boto3.resource('sqs')

# Get the queue
queue = sqs.get_queue_by_name(QueueName='test-modern-devops')

# Create a new message
response = queue.send_message(MessageBody='boto3', MessageAttributes={
    'Author': {
        'StringValue': 'Christian',
        'DataType': 'String'
    }
})

# The response is NOT a resource, but gives you a message ID and MD5
print(response.get('MessageId'))
print(response.get('MD5OfMessageBody'))