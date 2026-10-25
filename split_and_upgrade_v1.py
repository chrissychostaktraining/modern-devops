#!/usr/bin/env python3
"""Split and upgrade v1 Modern DevOps manuscript into structured Second Edition chapters."""
import re
import textwrap
from pathlib import Path

V1_PATH = Path(
    "/home/chris/Desktop/Mastering Modern DevOps_ A Comprehensive Guide to Infrastructure, Automation, and Cloud-Native Technologies.md"
)
CHAPTERS_DIR = Path("/home/chris/Desktop/modern-devops/chapters")

# Clean multi-line replacements keyed by v1 line number (1-indexed)
CODE_OVERRIDES = {
    1493: ("bash", "node -v\nnpm -v"),
    1512: ("bash", "node -v\nnpm -v"),
    1541: (
        "text",
        "$ aws configure\n"
        "AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE\n"
        "AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\n"
        "Default region name [None]: us-west-2\n"
        "Default output format [None]: json",
    ),
    1598: (
        "text",
        "/my-cdk-app\n"
        "├── bin\n"
        "│   └── my_cdk_app.py\n"
        "├── lib\n"
        "│   ├── vpc\n"
        "│   │   ├── __init__.py\n"
        "│   │   └── vpc_stack.py\n"
        "│   ├── ecs\n"
        "│   │   ├── __init__.py\n"
        "│   │   └── ecs_stack.py\n"
        "│   └── rds\n"
        "│       ├── __init__.py\n"
        "│       └── rds_stack.py\n"
        "├── tests\n"
        "│   ├── __init__.py\n"
        "│   └── test_my_cdk_app.py\n"
        "├── app.py\n"
        "├── cdk.json\n"
        "├── requirements.txt\n"
        "└── setup.py",
    ),
    1615: (
        "python",
        "from aws_cdk import (\n"
        "    App,\n"
        "    Stack,\n"
        "    aws_s3 as s3,\n"
        "    aws_sqs as sqs,\n"
        ")\n"
        "from constructs import Construct\n\n"
        "class MyCdkApp(Stack):\n"
        "    def __init__(\n"
        "        self, scope: Construct, id: str, **kwargs\n"
        "    ) -> None:\n"
        "        super().__init__(scope, id, **kwargs)\n"
        '        s3.Bucket(self, "MyBucket")\n'
        '        sqs.Queue(self, "MyQueue")\n\n'
        "app = App()\n"
        'MyCdkApp(app, "MyCdkApp")\n'
        "app.synth()",
    ),
    1628: (
        "python",
        "from aws_cdk import Stack, aws_s3 as s3\n"
        "from constructs import Construct\n\n"
        "class MyCdkAppStack(Stack):\n"
        "    def __init__(\n"
        "        self, scope: Construct, id: str, **kwargs\n"
        "    ) -> None:\n"
        "        super().__init__(scope, id, **kwargs)\n"
        '        s3.Bucket(self, "MyBucket")',
    ),
    1633: (
        "python",
        "import unittest\n"
        "from aws_cdk import App\n"
        "from aws_cdk.assertions import Template\n"
        "from my_cdk_app.my_cdk_app_stack import (\n"
        "    MyCdkAppStack,\n"
        ")\n\n"
        "class TestMyCdkAppStack(unittest.TestCase):\n"
        "    def setUp(self):\n"
        "        self.app = App()\n"
        "        self.stack = MyCdkAppStack(\n"
        '            self.app, "MyCdkAppStack"\n'
        "        )\n\n"
        "    def test_s3_bucket_created(self):\n"
        "        template = Template.from_stack(self.stack)\n"
        "        template.resource_count_is(\n"
        '            "AWS::S3::Bucket", 1\n'
        "        )\n\n"
        'if __name__ == "__main__":\n'
        "    unittest.main()",
    ),
    1659: (
        "python",
        "from aws_cdk import (\n"
        "    App,\n"
        "    Stack,\n"
        "    pipelines,\n"
        "    aws_codecommit as codecommit,\n"
        "    aws_codepipeline as codepipeline,\n"
        "    aws_codepipeline_actions as cpactions,\n"
        ")\n\n"
        "class MyCdkPipelineApp(App):\n"
        "    def __init__(self, **kwargs):\n"
        "        super().__init__(**kwargs)\n"
        '        stack = Stack(self, "MyStack")\n'
        "        repo = codecommit.Repository(\n"
        '            stack, "Repository",\n'
        '            repository_name="myrepository",\n'
        "        )\n"
        "        source_artifact = codepipeline.Artifact()\n"
        "        source_action = (\n"
        "            cpactions.CodeCommitSourceAction(\n"
        '                action_name="CodeCommit",\n'
        "                repository=repo,\n"
        "                output=source_artifact,\n"
        "            )\n"
        "        )\n"
        "        cdk_build = pipelines.SimpleSynthAction(\n"
        "            install_commands=[\n"
        '                "npm install -g aws-cdk"\n'
        "            ],\n"
        '            synth_command="cdk synth",\n'
        "            source_artifact=source_artifact,\n"
        "            cloud_assembly_artifact=(\n"
        "                codepipeline.Artifact()\n"
        "            ),\n"
        "        )\n"
        "        pipelines.CdkPipeline(\n"
        '            stack, "Pipeline",\n'
        "            cloud_assembly_artifact=(\n"
        "                cdk_build.cloud_assembly_artifact\n"
        "            ),\n"
        '            pipeline_name="MyPipeline",\n'
        "            source_action=source_action,\n"
        "            synth=cdk_build,\n"
        "        )\n\n"
        "app = MyCdkPipelineApp()\n"
        "app.synth()",
    ),
    1672: (
        "python",
        "from aws_cdk import (\n"
        "    App,\n"
        "    Stack,\n"
        "    aws_s3 as s3,\n"
        "    aws_lambda as _lambda,\n"
        ")\n\n"
        "class MyStack(Stack):\n"
        "    def __init__(self, app: App, id: str) -> None:\n"
        "        super().__init__(app, id)\n"
        '        bucket = s3.Bucket(self, "MyBucket")\n'
        "        handler = _lambda.Function(\n"
        '            self, "MyLambdaHandler",\n'
        "            runtime=_lambda.Runtime.PYTHON_3_11,\n"
        '            handler="index.handler",\n'
        "            code=_lambda.Code.from_inline(\n"
        '                "import os\\n"\n'
        '                "print(os.environ[\'BUCKET\'])"\n'
        "            ),\n"
        "            environment={\n"
        '                "BUCKET": bucket.bucket_name,\n'
        "            },\n"
        "        )\n"
        "        bucket.grant_read(handler)",
    ),
    1677: (
        "python",
        "from aws_cdk import (\n"
        "    App,\n"
        "    Stack,\n"
        "    aws_iam as iam,\n"
        "    aws_ec2 as ec2,\n"
        ")\n\n"
        "class MyStack(Stack):\n"
        "    def __init__(self, app: App, id: str) -> None:\n"
        "        super().__init__(app, id)\n"
        "        profile = iam.CfnInstanceProfile(\n"
        '            self, "InstanceProfile",\n'
        '            instance_profile_name="my_profile",\n'
        '            roles=["my_role_name"],\n'
        "        )\n"
        "        instance = ec2.CfnInstance(\n"
        '            self, "Instance",\n'
        '            image_id="ami-0abcdef1234567890",\n'
        '            instance_type="t3.micro",\n'
        "            iam_instance_profile=profile.ref,\n"
        "        )\n"
        "        instance.node.add_dependency(profile)",
    ),
    1692: (
        "python",
        "from aws_cdk import (\n"
        "    aws_s3 as s3,\n"
        "    aws_s3_deployment as s3deploy,\n"
        ")\n"
        "from constructs import Construct\n\n"
        "class StaticWebsiteConstruct(Construct):\n"
        "    def __init__(\n"
        "        self,\n"
        "        scope: Construct,\n"
        "        id: str,\n"
        "        website_dist_path: str,\n"
        "    ) -> None:\n"
        "        super().__init__(scope, id)\n"
        "        bucket = s3.Bucket(\n"
        '            self, "WebsiteBucket",\n'
        '            website_index_document="index.html",\n'
        "            public_read_access=True,\n"
        "        )\n"
        "        s3deploy.BucketDeployment(\n"
        '            self, "DeployWebsite",\n'
        "            sources=[\n"
        "                s3deploy.Source.asset(\n"
        "                    website_dist_path\n"
        "                )\n"
        "            ],\n"
        "            destination_bucket=bucket,\n"
        '            destination_key_prefix="/",\n'
        "        )",
    ),
    1697: (
        "python",
        "from aws_cdk import App, Stack\n\n"
        "app = App()\n"
        'stack = Stack(app, "MyStack")\n'
        "website = StaticWebsiteConstruct(\n"
        '    stack, "MyWebsite", "./dist"\n'
        ")\n"
        "app.synth()",
    ),
    1704: (
        "python",
        "from aws_cdk import Duration, aws_sqs as sqs\n"
        "from constructs import Construct\n\n"
        "class LongPollingQueueConstruct(sqs.Queue):\n"
        "    def __init__(\n"
        "        self, scope: Construct, id: str\n"
        "    ) -> None:\n"
        "        super().__init__(\n"
        "            scope, id,\n"
        "            visibility_timeout=Duration.seconds(30),\n"
        "            receive_message_wait_time=(\n"
        "                Duration.seconds(20)\n"
        "            ),\n"
        "        )",
    ),
    1719: (
        "python",
        "from aws_cdk import App, Stack\n\n"
        "app = App()\n"
        'stack = Stack(app, "MyStack")\n'
        "website1 = StaticWebsiteConstruct(\n"
        '    stack, "Website1", "./dist1"\n'
        ")\n"
        "website2 = StaticWebsiteConstruct(\n"
        '    stack, "Website2", "./dist2"\n'
        ")\n"
        "app.synth()",
    ),
    1755: ("python", "import boto3\n\ns3 = boto3.resource('s3')"),
    1764: ("python", "for bucket in s3.buckets.all():\n    print(bucket.name)"),
    1775: (
        "python",
        "response = s3.get_object(\n"
        "    Bucket='my-bucket',\n"
        "    Key='my-key'\n"
        ")\n"
        "print(response['Body'].read())",
    ),
    1786: (
        "python",
        "import boto3\n\n"
        "# Initialize the S3 client\n"
        "s3 = boto3.client('s3')\n\n"
        "# Create a new S3 bucket\n"
        "s3.create_bucket(Bucket='my-new-bucket')\n\n"
        "# Upload a file to the new bucket\n"
        "with open('myfile.txt', 'rb') as data:\n"
        "    s3.upload_fileobj(\n"
        "        data, 'my-new-bucket', 'myfile.txt'\n"
        "    )",
    ),
    1797: (
        "python",
        "import boto3\n\n"
        "# Initialize the Lambda client\n"
        "lambda_client = boto3.client('lambda')\n\n"
        "# Invoke a Lambda function\n"
        "response = lambda_client.invoke(\n"
        "    FunctionName='my-function',\n"
        "    InvocationType='RequestResponse',\n"
        '    Payload=b\'{"key1": "v1", "key2": "v2"}\',\n'
        ")\n\n"
        "# Print out the response\n"
        "print(response['Payload'].read())",
    ),
    1808: (
        "python",
        "import boto3\n\n"
        "# Initialize the DynamoDB resource\n"
        "dynamodb = boto3.resource('dynamodb')",
    ),
    1813: (
        "python",
        "# Create a new DynamoDB table\n"
        "table = dynamodb.create_table(\n"
        "    TableName='my-table',\n"
        "    KeySchema=[\n"
        "        {\n"
        "            'AttributeName': 'id',\n"
        "            'KeyType': 'HASH',\n"
        "        },\n"
        "    ],\n"
        "    AttributeDefinitions=[\n"
        "        {\n"
        "            'AttributeName': 'id',\n"
        "            'AttributeType': 'S',\n"
        "        },\n"
        "    ],\n"
        "    ProvisionedThroughput={\n"
        "        'ReadCapacityUnits': 5,\n"
        "        'WriteCapacityUnits': 5,\n"
        "    },\n"
        ")\n"
        "waiter = table.meta.client.get_waiter(\n"
        "    'table_exists'\n"
        ")\n"
        "waiter.wait(TableName='my-table')",
    ),
    1820: (
        "python",
        "# Insert an item into the table\n"
        "table.put_item(\n"
        "    Item={\n"
        "        'id': '1',\n"
        "        'name': 'John Doe',\n"
        "        'email': 'john@example.com',\n"
        "    }\n"
        ")",
    ),
    1840: (
        "python",
        "from aws_xray_sdk.core import xray_recorder\n"
        "from aws_xray_sdk.core import patch\n\n"
        "libraries = ['boto3']\n"
        "patch(libraries)",
    ),
    1847: (
        "python",
        "@xray_recorder.capture('My function')\n"
        "def lambda_handler(event, context):\n"
        "    # Your handler logic here\n"
        "    pass",
    ),
    1858: (
        "bash",
        "aws lambda update-function-configuration \\\n"
        "  --function-name my-function \\\n"
        "  --tracing-config Mode=Active",
    ),
    1910: (
        "yaml",
        "---\n"
        "- name: Install and start apache\n"
        "  hosts: webservers\n"
        "  tasks:\n"
        "    - name: Ensure package 'httpd' is installed\n"
        "      yum:\n"
        "        name: httpd\n"
        "        state: present\n"
        "    - name: Ensure service 'httpd' is running\n"
        "      service:\n"
        "        name: httpd\n"
        "        state: started",
    ),
    1927: (
        "yaml",
        "---\n"
        "- hosts: webservers\n"
        "  roles:\n"
        "    - role: apache",
    ),
    1948: (
        "yaml",
        "---\n"
        "- name: Install apache\n"
        "  yum:\n"
        "    name: httpd\n"
        "    state: present",
    ),
    2057: (
        "groovy",
        "pipeline {\n"
        "    agent any\n"
        "    stages {\n"
        "        stage('Build') {\n"
        "            steps {\n"
        "                echo 'Building..'\n"
        "                sh 'mvn clean install'\n"
        "            }\n"
        "        }\n"
        "    }\n"
        "}",
    ),
    2068: (
        "groovy",
        "pipeline {\n"
        "    agent any\n"
        "    stages {\n"
        "        stage('Build') {\n"
        "            steps {\n"
        "                echo 'Building..'\n"
        "                sh 'mvn clean install'\n"
        "            }\n"
        "        }\n"
        "        stage('Deploy') {\n"
        "            steps {\n"
        "                echo 'Deploying..'\n"
        "                sh 'cp target/myapp.war ' +\n"
        "                   '/path/to/tomcat/webapps/'\n"
        "            }\n"
        "        }\n"
        "    }\n"
        "}",
    ),
    2079: (
        "groovy",
        "pipeline {\n"
        "    agent any\n"
        "    stages {\n"
        "        stage('Build') {\n"
        "            steps {\n"
        "                echo 'Building..'\n"
        "                sh 'mvn clean install'\n"
        "            }\n"
        "        }\n"
        "        stage('Test') {\n"
        "            steps {\n"
        "                echo 'Testing..'\n"
        "                sh 'mvn test'\n"
        "            }\n"
        "        }\n"
        "        stage('Deploy to Staging') {\n"
        "            steps {\n"
        "                echo 'Deploying to staging..'\n"
        "                sh 'cp target/myapp.war ' +\n"
        "                   '/srv/staging/webapps/'\n"
        "            }\n"
        "        }\n"
        "        stage('Deploy to Production') {\n"
        "            steps {\n"
        "                echo 'Deploying to production..'\n"
        "                sh 'cp target/myapp.war ' +\n"
        "                   '/srv/prod/webapps/'\n"
        "            }\n"
        "        }\n"
        "    }\n"
        "}",
    ),
    2118: (
        "yaml",
        "stages:\n"
        "  - test\n"
        "  - build\n\n"
        "test:\n"
        "  stage: test\n"
        "  script: mvn test\n\n"
        "build:\n"
        "  stage: build\n"
        "  script: mvn package",
    ),
    2129: (
        "yaml",
        "stages:\n"
        "  - build\n"
        "  - test\n"
        "  - deploy\n\n"
        "build:\n"
        "  stage: build\n"
        "  script:\n"
        '    - echo "Building the application"\n'
        "    - mvn compile\n\n"
        "test:\n"
        "  stage: test\n"
        "  script:\n"
        '    - echo "Running tests"\n'
        "    - mvn test\n\n"
        "deploy_staging:\n"
        "  stage: deploy\n"
        "  script:\n"
        '    - echo "Deploying to staging"\n'
        "  environment:\n"
        "    name: staging\n"
        "    url: https://staging.example.com\n\n"
        "deploy_production:\n"
        "  stage: deploy\n"
        "  script:\n"
        '    - echo "Deploying to production"\n'
        "  environment:\n"
        "    name: production\n"
        "    url: https://www.example.com\n"
        "  when: manual\n"
        "  only:\n"
        "    - main",
    ),
    2150: (
        "yaml",
        "name: Node.js CI\n\n"
        "on: [push, pull_request]\n\n"
        "jobs:\n"
        "  build:\n"
        "    runs-on: ubuntu-latest\n"
        "    strategy:\n"
        "      matrix:\n"
        "        node-version: [18.x, 20.x, 22.x]\n"
        "    steps:\n"
        "      - uses: actions/checkout@v4\n"
        "      - name: Use Node.js ${{ matrix.node-version }}\n"
        "        uses: actions/setup-node@v4\n"
        "        with:\n"
        "          node-version: ${{ matrix.node-version }}\n"
        "      - run: npm ci\n"
        "      - run: npm run build --if-present\n"
        "      - run: npm test",
    ),
    2499: (
        "dockerfile",
        "# Use an official Python runtime as a base image\n"
        "FROM python:3.11-slim\n\n"
        "# Set the working directory in the container\n"
        "WORKDIR /app\n\n"
        "# Copy the current directory contents into /app\n"
        "COPY . /app\n\n"
        "# Install required packages from requirements.txt\n"
        "RUN pip install --no-cache-dir -r requirements.txt\n\n"
        "# Expose port 80 outside this container\n"
        "EXPOSE 80\n\n"
        "# Define environment variable\n"
        "ENV NAME=World\n\n"
        "# Run app.py when the container launches\n"
        'CMD ["python", "app.py"]',
    ),
    2540: (
        "dockerfile",
        "# First Stage: Install dependencies and build app\n"
        "FROM node:20-alpine AS builder\n"
        "WORKDIR /app\n"
        "COPY package*.json ./\n"
        "RUN npm ci --only=production\n\n"
        "# Second Stage: Create the lean final image\n"
        "FROM node:20-alpine\n"
        "WORKDIR /app\n\n"
        "# Create a non-root user and assign ownership\n"
        "RUN adduser -D appuser && chown -R appuser /app\n"
        "USER appuser\n\n"
        "COPY --from=builder /app ./\n"
        "EXPOSE 8080\n"
        'CMD ["node", "server.js"]',
    ),
    2708: (
        "bash",
        "kubectl scale deployment my-deployment --replicas=0\n"
        "kubectl set image deployment/my-deployment \\\n"
        "  my-container=my-image:v2\n"
        "kubectl scale deployment my-deployment \\\n"
        "  --replicas=<desired_replica_count>",
    ),
    2747: (
        "yaml",
        "apiVersion: v1\n"
        "kind: Service\n"
        "metadata:\n"
        "  name: my-app-service\n"
        "spec:\n"
        "  selector:\n"
        "    app: my-app\n"
        "    version: blue\n"
        "  ports:\n"
        "    - protocol: TCP\n"
        "      port: 80\n"
        "      targetPort: 8080",
    ),
    2752: (
        "yaml",
        "apiVersion: v1\n"
        "kind: Service\n"
        "metadata:\n"
        "  name: my-app-service-green\n"
        "spec:\n"
        "  selector:\n"
        "    app: my-app\n"
        "    version: green\n"
        "  ports:\n"
        "    - protocol: TCP\n"
        "      port: 80\n"
        "      targetPort: 8080",
    ),
    2757: (
        "yaml",
        "apiVersion: apps/v1\n"
        "kind: Deployment\n"
        "metadata:\n"
        "  name: my-app-blue\n"
        "spec:\n"
        "  selector:\n"
        "    matchLabels:\n"
        "      app: my-app\n"
        "      version: blue\n"
        "  template:\n"
        "    metadata:\n"
        "      labels:\n"
        "        app: my-app\n"
        "        version: blue\n"
        "    spec:\n"
        "      containers:\n"
        "        - name: my-app\n"
        "          image: my-app:v1\n"
        "          ports:\n"
        "            - containerPort: 8080",
    ),
    2764: (
        "bash",
        "kubectl patch service my-app-service \\\n"
        '  -p \'{"spec":{"selector":{"version":"green"}}}\'',
    ),
    3096: (
        "yaml",
        "scrape_configs:\n"
        "  - job_name: 'webapp'\n"
        "    static_configs:\n"
        "      - targets: ['localhost:9090']",
    ),
    3159: (
        "bash",
        "docker run -d --name jaeger \\\n"
        "  -e COLLECTOR_ZIPKIN_HOST_PORT=:9411 \\\n"
        "  -p 5775:5775/udp -p 6831:6831/udp \\\n"
        "  -p 6832:6832/udp -p 5778:5778 \\\n"
        "  -p 16686:16686 -p 14268:14268 \\\n"
        "  -p 14250:14250 -p 9411:9411 \\\n"
        "  jaegertracing/all-in-one:1.57",
    ),
    3194: (
        "text",
        "input {\n"
        "  file {\n"
        '    path => "/path/to/log/file"\n'
        '    start_position => "beginning"\n'
        "  }\n"
        "}\n\n"
        "filter {\n"
        "  # Log transformations go here\n"
        "}\n\n"
        "output {\n"
        "  elasticsearch {\n"
        '    hosts => ["localhost:9200"]\n'
        "  }\n"
        "}",
    ),
    3476: (
        "nginx",
        "location / {\n"
        "    proxy_pass http://localhost:8080;\n"
        "}",
    ),
    3485: (
        "nginx",
        "upstream backend {\n"
        "    server backend1.example.com;\n"
        "    server backend2.example.com;\n"
        "    server backend3.example.com;\n"
        "}\n\n"
        "server {\n"
        "    location / {\n"
        "        proxy_pass http://backend;\n"
        "    }\n"
        "}",
    ),
    3520: (
        "bash",
        "sudo apt update\n"
        "sudo apt install -y apt-transport-https \\\n"
        "  ca-certificates curl software-properties-common\n"
        "curl -fsSL https://download.docker.com/linux/ubuntu/gpg \\\n"
        "  | sudo apt-key add -\n"
        "sudo apt update && sudo apt install -y docker-ce",
    ),
    3536: (
        "yaml",
        "static_resources:\n"
        "  listeners:\n"
        "    - name: listener_0\n"
        "      address:\n"
        "        socket_address:\n"
        "          address: 0.0.0.0\n"
        "          port_value: 10000\n"
        "      filter_chains:\n"
        "        - filters:\n"
        "            - name: envoy.http_connection_manager\n"
        "              typed_config:\n"
        "                codec_type: AUTO\n"
        "                stat_prefix: ingress_http\n"
        "                route_config:\n"
        "                  name: local_route\n"
        "                  virtual_hosts:\n"
        "                    - name: local_service\n"
        '                      domains: ["*"]\n'
        "                      routes:\n"
        "                        - match: { prefix: \"/\" }\n"
        "                          route:\n"
        "                            cluster: service_google\n"
        "  clusters:\n"
        "    - name: service_google\n"
        "      connect_timeout: 0.25s\n"
        "      type: LOGICAL_DNS\n"
        "      lb_policy: ROUND_ROBIN",
    ),
    3599: (
        "bash",
        "curl -L https://istio.io/downloadIstio \\\n"
        "  | ISTIO_VERSION=1.22.0 sh -",
    ),
    3721: (
        "python",
        "import os\n"
        "import uuid\n"
        "import boto3\n"
        "from PIL import Image\n\n"
        "s3 = boto3.client('s3')\n\n"
        "def resize_image(image_path, resized_path):\n"
        "    with Image.open(image_path) as img:\n"
        "        img.thumbnail(\n"
        "            tuple(x // 2 for x in img.size)\n"
        "        )\n"
        "        img.save(resized_path)\n\n"
        "def lambda_handler(event, context):\n"
        "    rec = event['Records'][0]['s3']\n"
        "    bucket = rec['bucket']['name']\n"
        "    key = rec['object']['key']\n"
        "    dl_path = f'/tmp/{uuid.uuid4()}-{key}'\n"
        "    up_path = f'/tmp/resized-{key}'\n"
        "    s3.download_file(bucket, key, dl_path)\n"
        "    resize_image(dl_path, up_path)\n"
        "    s3.upload_file(\n"
        "        up_path, f'{bucket}-resized', key\n"
        "    )",
    ),
    3754: (
        "python",
        "def lambda_handler(event, context):\n"
        "    print('Hello, AWS Lambda!')\n"
        "    return 'Hello, AWS Lambda!'",
    ),
    3798: (
        "bash",
        "aws lambda create-function \\\n"
        "  --function-name my_lambda \\\n"
        "  --zip-file fileb://function.zip \\\n"
        "  --handler lambda_handler.handler \\\n"
        "  --runtime python3.11 \\\n"
        "  --role arn:aws:iam::123456789012:role/exec_role",
    ),
    3831: (
        "bash",
        "aws lambda update-function-code \\\n"
        "  --function-name my_lambda \\\n"
        "  --zip-file fileb://function.zip",
    ),
    3860: (
        "javascript",
        "exports.helloWorld = (req, res) => {\n"
        "  res.send('Hello, Google Cloud Functions!');\n"
        "};",
    ),
    3871: (
        "bash",
        "gcloud functions deploy helloWorld \\\n"
        "  --runtime nodejs20 \\\n"
        "  --trigger-http \\\n"
        "  --allow-unauthenticated",
    ),
    3910: (
        "javascript",
        "module.exports = async function (context, req) {\n"
        "    context.res = {\n"
        "        status: 200,\n"
        '        body: "Hello, Azure Functions!"\n'
        "    };\n"
        "};",
    ),
    3921: (
        "bash",
        "az functionapp create \\\n"
        "  --resource-group myResourceGroup \\\n"
        "  --os-type Linux \\\n"
        "  --consumption-plan-location westus \\\n"
        "  --runtime node \\\n"
        "  --name <APP_NAME> \\\n"
        "  --storage-account <STORAGE_NAME>",
    ),
    4017: (
        "hcl",
        'provider "aws" {\n'
        '  region = "us-west-2"\n'
        "}\n\n"
        'resource "aws_instance" "example" {\n'
        '  ami           = "ami-0c94855ba95c574c8"\n'
        '  instance_type = "t3.micro"\n\n'
        "  tags = {\n"
        '    Name = "example-instance"\n'
        "  }\n"
        "}",
    ),
    4650: (
        "ruby",
        "control 'example-1' do\n"
        "  impact 1.0\n"
        "  title 'Check if /etc/passwd exists'\n"
        "  desc 'The /etc/passwd file should exist'\n"
        "  describe file('/etc/passwd') do\n"
        "    it { should exist }\n"
        "  end\n"
        "end",
    ),
    4703: (
        "go",
        "package test\n\n"
        "import (\n"
        '\t"testing"\n'
        '\t"github.com/gruntwork-io/terratest/modules/terraform"\n'
        ")\n\n"
        "func TestMyModule(t *testing.T) {\n"
        "\topts := &terraform.Options{\n"
        '\t\tTerraformDir: "../mymodule",\n'
        "\t}\n"
        "\tdefer terraform.Destroy(t, opts)\n"
        "\tterraform.InitAndApply(t, opts)\n"
        "}",
    ),
}

# Mermaid diagrams to inject into existing chapters (20 diagrams across files 03-22)
CHAPTER_MERMAID_DIAGRAMS = {
    "03-introduction-understanding-modern-devops.md": """```mermaid
flowchart LR
    Plan["Plan & Design"]
    Code["Develop & Commit"]
    Build["Build & Verify"]
    Release["Deploy & Release"]
    Operate["Operate & Observe"]
    Feedback["Continuous Feedback"]
    Plan --> Code --> Build --> Release --> Operate --> Feedback --> Plan
```""",
    "04-introduction-the-evolution-of-devops.md": """```mermaid
flowchart LR
    Waterfall["1990s: Waterfall Silos"]
    Agile["2001: Agile Manifesto"]
    DevOps["2009: DevOps Movement"]
    CloudNative["2015+: Cloud-Native & GitOps"]
    PlatformAI["2024+: IDPs, eBPF & AI SRE"]
    Waterfall --> Agile --> DevOps --> CloudNative --> PlatformAI
```""",
    "05-chapter-01-mastering-aws-cdk-infrastructure-as-code.md": """```mermaid
flowchart TD
    App["CDK App (Python / TypeScript)"]
    Stack["CDK Stack (VPC, ECS, RDS)"]
    Constructs["L1 / L2 / L3 Constructs"]
    Synth["cdk synth (Cloud Assembly)"]
    CFN["AWS CloudFormation Template"]
    AWS["Provisioned AWS Resources"]
    App --> Stack --> Constructs --> Synth --> CFN --> AWS
```""",
    "06-chapter-02-aws-sdk-developing-with-the-cloud-in-mind.md": """```mermaid
flowchart LR
    App["Python Application (Boto3)"]
    Creds["IAM Role / Credential Chain"]
    S3["Amazon S3 Bucket"]
    Lambda["AWS Lambda Function"]
    Dynamo["Amazon DynamoDB Table"]
    XRay["AWS X-Ray Telemetry"]
    App --> Creds
    Creds --> S3
    Creds --> Lambda
    Creds --> Dynamo
    Lambda --> XRay
```""",
    "07-chapter-03-configuration-management-streamlining-your-infrastructure.md": """```mermaid
flowchart LR
    Git["Git Config Repo"]
    Control["Ansible Control Node"]
    Inv["Dynamic Inventory"]
    Playbook["Idempotent Playbooks & Roles"]
    Web["Web Fleet"]
    DB["Database Fleet"]
    Git --> Control
    Inv --> Control
    Control --> Playbook
    Playbook --> Web
    Playbook --> DB
```""",
    "08-chapter-04-cicd-pipelines-accelerate-your-releases.md": """```mermaid
flowchart LR
    Commit["Git Push / PR"]
    CI["Build & Unit Tests"]
    SAST["SAST & Image Scan"]
    Artifact["Signed OCI Artifact"]
    Staging["Staging Canary"]
    Prod["Production Rollout"]
    Commit --> CI --> SAST --> Artifact --> Staging --> Prod
```""",
    "09-chapter-05-artifact-repositories-centralize-and-secure-your-packages.md": """```mermaid
flowchart LR
    CI["CI Build Runner"]
    Scan["Vulnerability & License Gate"]
    Repo["Artifact Repository (Artifactory / Nexus / CodeArtifact)"]
    Sign["Cryptographic Signature"]
    K8s["Production Kubernetes Cluster"]
    CI --> Scan --> Repo --> Sign --> K8s
```""",
    "10-chapter-06-docker-containers-and-containerd.md": """```mermaid
flowchart TD
    Stage1["Stage 1: Builder Image (Compiler & Dev Deps)"]
    Artifact["Compiled Application Binary"]
    Stage2["Stage 2: Minimal Runtime Image (Non-Root User)"]
    CRI["containerd Runtime (OCI Spec)"]
    Kernel["Linux Kernel Namespaces & cgroups"]
    Stage1 --> Artifact --> Stage2 --> CRI --> Kernel
```""",
    "11-chapter-07-container-orchestration-kubernetes-and-beyond.md": """```mermaid
flowchart TD
    API["kube-apiserver"]
    Etcd["etcd State Store"]
    Sched["kube-scheduler"]
    CM["kube-controller-manager"]
    Kubelet["Worker Node: kubelet & containerd"]
    Pods["Application Pods (Blue/Green & Canary)"]
    API --> Etcd
    API --> Sched
    API --> CM
    API --> Kubelet --> Pods
```""",
    "12-chapter-08-observability-monitoring-tracing-and-logging.md": """```mermaid
flowchart LR
    Services["Instrumented Microservices"]
    Prom["Prometheus (Metrics)"]
    Jaeger["Jaeger / OTel (Traces)"]
    ELK["ELK / OpenSearch (Logs)"]
    Grafana["Grafana Unified Dashboards & Alerts"]
    Services --> Prom --> Grafana
    Services --> Jaeger --> Grafana
    Services --> ELK --> Grafana
```""",
    "13-chapter-09-securing-your-devops-pipeline.md": """```mermaid
flowchart LR
    Dev["Pre-Commit & Secret Scan"]
    SAST["SAST & SCA Dependency Audit"]
    Vault["HashiCorp Vault / AWS Secrets Manager"]
    DAST["DAST & Policy Gate"]
    Runtime["Runtime Compliance & Audit"]
    Dev --> SAST --> Vault --> DAST --> Runtime
```""",
    "14-chapter-10-proxies-load-balancers-and-service-meshes-demystified.md": """```mermaid
flowchart LR
    Client["External Client"]
    Ingress["NGINX / Envoy Edge Proxy"]
    Control["Istio Control Plane (istiod)"]
    SvcA["Service A + Envoy Proxy"]
    SvcB["Service B + Envoy Proxy"]
    Client --> Ingress --> SvcA
    SvcA <-->|"mTLS & Telemetry"| SvcB
    Control -.->|"xDS Config & Certs"| SvcA
    Control -.->|"xDS Config & Certs"| SvcB
```""",
    "15-chapter-11-serverless-applications-the-future-of-cloud-computing.md": """```mermaid
flowchart LR
    Event["API Gateway / S3 Event / EventBridge"]
    Func["Serverless Function (AWS Lambda / GCF / Azure)"]
    Queue["SQS / PubSub Async Buffer"]
    Data["Managed NoSQL (DynamoDB)"]
    Trace["Distributed Trace & CloudWatch"]
    Event --> Func --> Queue --> Data
    Func --> Trace
```""",
    "16-chapter-12-infrastructure-as-code-and-best-practices.md": """```mermaid
flowchart LR
    VCS["Git Version Control & PR Review"]
    Plan["Declarative Plan (Terraform / Pulumi / CloudFormation)"]
    Policy["Shift-Left Security & Least-Privilege Check"]
    State["Locked Remote State Backend"]
    Cloud["Provisioned Cloud Infrastructure"]
    VCS --> Plan --> Policy --> State --> Cloud
```""",
    "17-chapter-13-infrastructure-and-application-monitoring.md": """```mermaid
flowchart TD
    Infra["Host, Network & Kubernetes Telemetry"]
    APM["Application APM & Distributed Traces"]
    RUM["Synthetic & Real-User Monitoring (RUM)"]
    Engine["Unified Analytics (Datadog / New Relic / AppDynamics)"]
    SLO["SLO Burn-Rate Alerting"]
    Infra --> Engine
    APM --> Engine
    RUM --> Engine
    Engine --> SLO
```""",
    "18-chapter-14-gitops-and-infrastructure-synchronization.md": """```mermaid
flowchart LR
    Dev["Engineer Pull Request"]
    Git["Git Repository (Desired State)"]
    Controller["Argo CD / Flux Reconciler"]
    Live["Kubernetes Cluster (Live State)"]
    Drift["Automated Drift Detection & Self-Healing"]
    Dev --> Git --> Controller --> Live --> Drift --> Controller
```""",
    "19-chapter-15-infrastructure-testing-and-validation.md": """```mermaid
flowchart LR
    Code["IaC Module (Terraform / Chef / Ansible)"]
    Kitchen["Test Kitchen Ephemeral Sandbox"]
    Terratest["Terratest Automated Go Harness"]
    InSpec["Chef InSpec Compliance Profile"]
    Gate["Production Promotion Gate"]
    Code --> Kitchen --> Terratest --> InSpec --> Gate
```""",
    "20-chapter-16-cloud-native-development-and-multi-cloud-strategies.md": """```mermaid
flowchart TD
    Control["Unified Multi-Cloud IaC (Terraform / Pulumi)"]
    BFF["Backends for Frontends (BFF) & Circuit Breakers"]
    AWS["AWS Cloud Region (EKS / RDS)"]
    GCP["Google Cloud Region (GKE / Spanner)"]
    Azure["Azure Cloud Region (AKS / CosmosDB)"]
    Control --> BFF
    BFF --> AWS
    BFF --> GCP
    BFF --> Azure
```""",
    "21-chapter-17-infrastructure-automation-and-orchestration.md": """```mermaid
flowchart LR
    Trigger["Schedule / Event / ChatOps Trigger"]
    Airflow["Apache Airflow DAG Orchestrator"]
    Tower["Ansible Automation Controller (RBAC)"]
    Rundeck["Rundeck Self-Service Runbooks"]
    Targets["Multi-Cloud & Hybrid Targets"]
    Trigger --> Airflow --> Tower --> Rundeck --> Targets
```""",
    "22-chapter-18-incident-management-and-on-call-best-practices.md": """```mermaid
flowchart LR
    Alert["Monitoring Alert (Prometheus / Datadog)"]
    Router["PagerDuty / Opsgenie Deduplication & Routing"]
    OnCall["Primary On-Call Responder"]
    WarRoom["Collaborative Incident War Room & Runbook"]
    Postmortem["Blameless Postmortem & Action Items"]
    Alert --> Router --> OnCall --> WarRoom --> Postmortem
```""",
}


def unescape_google_docs(text: str) -> str:
    """Clean Google Docs Markdown export artifacts."""
    text = text.replace(r"https\://", "https://").replace(r"http\://", "http://")
    text = text.replace(r"www\.", "www.")
    text = text.replace(r"\!", "!")
    text = text.replace(r"\-", "-")
    text = text.replace(r"\_", "_")
    text = text.replace(r"\#", "#")
    text = text.replace(r"\=", "=")
    text = text.replace(r"\+", "+")
    text = text.replace(r"\[", "[").replace(r"\]", "]")
    text = text.replace(r"\<", "<").replace(r"\>", ">")
    text = text.replace(r"\*", "*")
    text = text.replace(r"\&", "&")
    text = text.replace(r"\$", "$")
    text = text.replace(r"\|", "|")
    return text


def wrap_cmd(cmd: str, width: int = 55) -> str:
    if len(cmd) <= width:
        return cmd
    lines = textwrap.wrap(
        cmd, width=width - 2, break_long_words=False, break_on_hyphens=False
    )
    if len(lines) <= 1:
        return cmd
    return " \\\n  ".join(lines)


def clean_section_lines(raw_lines: list[str], start_line_1idx: int) -> str:
    out = []
    i = 0
    while i < len(raw_lines):
        line_no = start_line_1idx + i
        line = raw_lines[i].rstrip("\r\n")

        # Skip empty headings like `# ` or `## `
        if re.match(r"^#{1,6}\s*$", line.strip()):
            i += 1
            continue

        # Convert single-row Google Docs code tables `| ... |\n| :---- |`
        if (
            line.startswith("|")
            and i + 1 < len(raw_lines)
            and re.match(r"^\|\s*:?-{2,}", raw_lines[i + 1])
        ):
            if line_no in CODE_OVERRIDES:
                lang, code_body = CODE_OVERRIDES[line_no]
            else:
                cell = line.strip()[1:-1].strip().replace("\x0b", "\n")
                cell = unescape_google_docs(cell)
                lang = "bash"
                code_body = "\n".join(
                    wrap_cmd(subline, 55) for subline in cell.split("\n")
                )
            out.append(f"```{lang}")
            out.append(code_body)
            out.append("```")
            i += 2
            continue

        # Strip heading anchor IDs `{#...}` and fix `21.3`
        if line.startswith("#"):
            line = re.sub(r"\s*\{#[^}]+\}", "", line)
            line = line.replace(
                "## 21.3 Cloud-Native Design Patterns",
                "## Cloud-Native Design Patterns",
            )
            line = unescape_google_docs(line).replace("\x0b", "\n")
            out.append(line.strip())
            i += 1
            continue

        line = unescape_google_docs(line).replace("\x0b", "\n")
        out.append(line)
        i += 1

    text = "\n".join(out).strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def build_front_matter() -> str:
    return """# Mastering Modern DevOps: A Comprehensive Guide to Infrastructure, Automation, and Cloud-Native Technologies (Second Edition)

## About the Author

**Christian Chostak** is a seasoned DevOps architect, cloud-native systems engineer, and technical leader with well over a decade of hands-on experience designing, automating, and securing resilient production infrastructure. Throughout his career, he has been instrumental in driving high-velocity DevOps, Platform Engineering, and DevSecOps transformations across industries ranging from hyper-growth technology startups to global multinational enterprises. Christian's deep technical expertise spans Infrastructure as Code (AWS CDK, Terraform, Pulumi, Crossplane), cloud-native container orchestration (Kubernetes, Amazon EKS, Cilium eBPF), automated CI/CD and GitOps delivery pipelines, OpenTelemetry observability, and cryptographic software supply chain security.

Beyond his architecture and engineering work in the field, Christian is deeply committed to technical education and open knowledge sharing within the global cloud-native community. He is a frequent speaker at industry conferences and technical symposiums, where he shares practical insights from real-world production incidents and large-scale cloud migrations. His passion for engineering mentorship extends to guiding software developers, systems administrators, and Site Reliability Engineers (SREs) in mastering modern cloud-native craftsmanship.

Christian holds multiple top-tier industry certifications, including **AWS Certified DevOps Engineer – Professional** and **Certified Kubernetes Administrator (CKA)**, and earned a **Master's degree in Software Engineering** from IPP.

In this **Second Edition** of *Mastering Modern DevOps: A Comprehensive Guide to Infrastructure, Automation, and Cloud-Native Technologies*, Christian brings together foundational DevOps principles and the latest cloud-native breakthroughs—including Internal Developer Platforms (IDPs), eBPF kernel networking, OpenTelemetry pipelines, AI-augmented SRE, and SLSA/Sigstore supply chain security—to provide a definitive desk reference for modern engineering organizations.

## Preface to the Second Edition

*Mastering Modern DevOps: A Comprehensive Guide to Infrastructure, Automation, and Cloud-Native Technologies (Second Edition)* is an end-to-end engineering blueprint designed for practitioners and technical leaders aiming to master the full lifecycle of cloud-native infrastructure and software delivery.

Since the publication of the First Edition, the cloud-native ecosystem has undergone a profound architectural shift. While Infrastructure as Code (IaC), CI/CD automation, Docker containers, Kubernetes orchestration, and GitOps remain the bedrock of high-performing engineering teams, four major paradigm shifts have redefined production operations:

1. **Platform Engineering and Internal Developer Platforms (Chapter 19)**: Organizations have evolved from fragmented "you build it, you run it" ticket queues to product-managed Internal Developer Platforms (IDPs) powered by **Backstage**, **Crossplane**, and **Kratix** that provide paved "Golden Paths" and reduce developer cognitive load.
2. **eBPF Cloud-Native Networking and Sidecarless Service Meshes (Chapter 20)**: Linux kernel **Extended Berkeley Packet Filter (eBPF)** data planes with **Cilium**, **Hubble**, **Tetragon**, and **Istio Ambient Mode** have eliminated traditional iptables bottlenecks and heavy per-pod sidecar proxy overhead while enforcing kernel-level zero-trust security.
3. **OpenTelemetry Collector Pipelines and AI-Augmented SRE (Chapter 21)**: Proprietary telemetry agents have converged onto **OpenTelemetry (OTel)** with zero-code eBPF auto-instrumentation, tail-based sampling, continuous eBPF profiling, and **AI-augmented Site Reliability Engineering (AIOps)** for automated root-cause correlation.
4. **Software Supply Chain Security with SLSA and Sigstore (Chapter 22)**: High-profile upstream compromises have made verifiable build provenance (**SLSA Build Level 3**), keyless OIDC artifact signing (**Sigstore Cosign**, **Fulcio**, and **Rekor**), automated **CycloneDX/SPDX SBOMs**, and **Kyverno** admission verification mandatory controls in modern Kubernetes clusters.

```mermaid
flowchart TD
    Foundations["Foundations & Cloud IaC (Ch 1-3: AWS CDK, SDK & Ansible)"]
    Delivery["CI/CD, Registries & Containers (Ch 4-7: Pipelines, Docker & Kubernetes)"]
    OpsSec["Observability, DevSecOps, Mesh & Serverless (Ch 8-11)"]
    Scale["Enterprise IaC, GitOps, Testing & Incident Response (Ch 12-18)"]
    V2New["Second Edition Cloud-Native Frontier (Ch 19-22: IDPs, eBPF, OTel/AI SRE & SLSA)"]
    Foundations --> Delivery --> OpsSec --> Scale --> V2New
```

Starting with the historical foundations and cultural pillars of modern DevOps, this book guides you progressively through AWS CDK, AWS SDK (Boto3), Ansible configuration management, Jenkins/GitLab/GitHub Actions CI/CD pipelines, artifact repositories, Docker and containerd, Kubernetes/ECS/Swarm orchestration, Prometheus/Grafana/Jaeger/ELK observability, DevSecOps secrets management, NGINX/Envoy/Istio service meshes, multi-cloud serverless architectures, Terraform/Pulumi IaC testing (Test Kitchen, InSpec, Terratest), Argo CD/Flux GitOps, Airflow/Rundeck automation, and PagerDuty/Opsgenie incident response—before culminating in four comprehensive new chapters covering the modern cloud-native frontier.
"""


def build_reader_guide(raw_lines: list[str]) -> str:
    body = clean_section_lines(raw_lines[24:54], 25)
    body = body.replace(
        "# Who Should Read This Book",
        "# Reader Guide: Who Should Read This Book and How to Use It\n\n## Who Should Read This Book",
    )
    body = body.replace("# How to Read This Book", "## How to Read This Book")
    return body


def inject_diagram_after_first_heading(markdown_text: str, diagram_block: str) -> str:
    """Insert a Mermaid diagram after the introductory paragraphs following the H1 heading."""
    lines = markdown_text.splitlines()
    # Find the first H2 (`## `) line to insert the architecture diagram right before it
    for idx, line in enumerate(lines):
        if line.startswith("## "):
            return (
                "\n".join(lines[:idx]).rstrip()
                + "\n\n"
                + diagram_block.strip()
                + "\n\n"
                + "\n".join(lines[idx:])
            )
    return markdown_text + "\n\n" + diagram_block.strip()


def main() -> None:
    CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)
    with V1_PATH.open("r", encoding="utf-8") as fh:
        raw_lines = [ln.rstrip("\r\n") for ln in fh.readlines()]

    # 01: Front Matter & Preface
    (CHAPTERS_DIR / "01-preface-and-front-matter.md").write_text(
        build_front_matter().strip() + "\n", encoding="utf-8"
    )

    # 02: Reader Guide
    (CHAPTERS_DIR / "02-reader-guide-and-book-structure.md").write_text(
        build_reader_guide(raw_lines).strip() + "\n", encoding="utf-8"
    )

    # Slices for files 03 through 22:
    # Tuple: (filename, new_h1_title, start_line_1idx, end_line_1idx_inclusive, sub_h1_replacements)
    chapter_specs = [
        (
            "03-introduction-understanding-modern-devops.md",
            "# Introduction: Understanding Modern DevOps",
            1349,
            1399,
            {},
        ),
        (
            "04-introduction-the-evolution-of-devops.md",
            "# The Evolution of DevOps: From Silos to Cloud-Native Engineering",
            1400,
            1456,
            {},
        ),
        (
            "05-chapter-01-mastering-aws-cdk-infrastructure-as-code.md",
            "# Chapter 1: Mastering AWS CDK: Infrastructure as Code",
            1457,
            1733,
            {},
        ),
        (
            "06-chapter-02-aws-sdk-developing-with-the-cloud-in-mind.md",
            "# Chapter 2: AWS SDK: Developing with the Cloud in Mind",
            1734,
            1866,
            {},
        ),
        (
            "07-chapter-03-configuration-management-streamlining-your-infrastructure.md",
            "# Chapter 3: Configuration Management: Streamlining Your Infrastructure",
            1867,
            1994,
            {},
        ),
        (
            "08-chapter-04-cicd-pipelines-accelerate-your-releases.md",
            "# Chapter 4: CI/CD Pipelines: Accelerate Your Releases",
            1995,
            2210,
            {},
        ),
        (
            "09-chapter-05-artifact-repositories-centralize-and-secure-your-packages.md",
            "# Chapter 5: Artifact Repositories: Centralize and Secure Your Packages",
            2211,
            2416,
            {},
        ),
        (
            "10-chapter-06-docker-containers-and-containerd.md",
            "# Chapter 6: Docker Containers and Containerd: Your Path to Containerization",
            2417,
            2544,
            {},
        ),
        (
            "11-chapter-07-container-orchestration-kubernetes-and-beyond.md",
            "# Chapter 7: Container Orchestration: Kubernetes and Beyond",
            2545,
            3044,
            {},
        ),
        (
            "12-chapter-08-observability-monitoring-tracing-and-logging.md",
            "# Chapter 8: Observability: Monitoring, Tracing, and Logging",
            3045,
            3208,
            {},
        ),
        (
            "13-chapter-09-securing-your-devops-pipeline.md",
            "# Chapter 9: Securing Your DevOps Pipeline",
            3209,
            3406,
            {},
        ),
        (
            "14-chapter-10-proxies-load-balancers-and-service-meshes-demystified.md",
            "# Chapter 10: Proxies, Load Balancers, and Service Meshes Demystified",
            3407,
            3686,
            {},
        ),
        (
            "15-chapter-11-serverless-applications-the-future-of-cloud-computing.md",
            "# Chapter 11: Serverless Applications: The Future of Cloud Computing",
            3687,
            3950,
            {},
        ),
        (
            "16-chapter-12-infrastructure-as-code-and-best-practices.md",
            "# Chapter 12: Infrastructure as Code: Foundations, Tooling, and Best Practices",
            3951,
            4159,
            {
                "# IaC Best Practices: Version Control, Testing, and Security": "## IaC Best Practices: Version Control, Testing, and Security"
            },
        ),
        (
            "17-chapter-13-infrastructure-and-application-monitoring.md",
            "# Chapter 13: Infrastructure and Application Monitoring",
            4160,
            4353,
            {},
        ),
        (
            "18-chapter-14-gitops-and-infrastructure-synchronization.md",
            "# Chapter 14: GitOps and Infrastructure Synchronization",
            4354,
            4497,
            {},
        ),
        (
            "19-chapter-15-infrastructure-testing-and-validation.md",
            "# Chapter 15: Infrastructure Testing and Validation",
            4498,
            4711,
            {},
        ),
        (
            "20-chapter-16-cloud-native-development-and-multi-cloud-strategies.md",
            "# Chapter 16: Cloud-Native Development Patterns and Multi-Cloud Strategies",
            4712,
            4875,
            {
                "# Multi-Cloud Strategies and Management": "## Multi-Cloud Strategies and Management"
            },
        ),
        (
            "21-chapter-17-infrastructure-automation-and-orchestration.md",
            "# Chapter 17: Infrastructure Automation and Orchestration",
            4876,
            5075,
            {},
        ),
        (
            "22-chapter-18-incident-management-and-on-call-best-practices.md",
            "# Chapter 18: Incident Management and On-Call Best Practices",
            5076,
            5247,
            {},
        ),
    ]

    for fname, new_h1, start_1idx, end_1idx, sub_repls in chapter_specs:
        sliced = raw_lines[start_1idx - 1 : end_1idx]
        cleaned = clean_section_lines(sliced, start_1idx)
        # Replace first line (original H1) with new_h1
        cleaned_lines = cleaned.splitlines()
        cleaned_lines[0] = new_h1
        text = "\n".join(cleaned_lines)
        for old_h, new_h in sub_repls.items():
            text = text.replace(old_h, new_h)
        if fname in CHAPTER_MERMAID_DIAGRAMS:
            text = inject_diagram_after_first_heading(
                text, CHAPTER_MERMAID_DIAGRAMS[fname]
            )
        out_path = CHAPTERS_DIR / fname
        out_path.write_text(text.strip() + "\n", encoding="utf-8")
        print(f"Wrote {fname} ({len(text.split())} words)")


if __name__ == "__main__":
    main()
