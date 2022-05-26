import boto3

# Let's use Amazon S3
s3 = boto3.resource('s3')
ec2 = boto3.client('ec2')

# Print out bucket names
for bucket in s3.buckets.all():
    print(bucket.name)

# Print EC2 instances
response = ec2.describe_instances()
print(response)