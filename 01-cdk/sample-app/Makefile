ACC=$(shell aws sts get-caller-identity | jq .Account)
EU_TASK_DESIRED_COUNT?=2
USA_TASK_DESIRED_COUNT?=5

synth:
	export TASK_DESIRED_COUNT=$(EU_TASK_DESIRED_COUNT) REGION=eu-west-1 ACCOUNT=$(ACC) && cdk synth --parameters TaskMemoryLimit=1024
	export TASK_DESIRED_COUNT=$(USA_TASK_DESIRED_COUNT) REGION=us-east-1 ACCOUNT=$(ACC) && cdk synth --parameters TaskMemoryLimit=1024

deploy:
	cdk deploy --parameters TaskMemoryLimit=1024 --all

deploy-eu:
	export TASK_DESIRED_COUNT=$(EU_TASK_DESIRED_COUNT) REGION=eu-west-1 ACCOUNT=$(ACC) && cdk synth --parameters TaskMemoryLimit=1024 && cdk deploy --parameters TaskMemoryLimit=1024 --all

deploy-usa:
	export TASK_DESIRED_COUNT=$(USA_TASK_DESIRED_COUNT) REGION=eu-west-1 ACCOUNT=$(ACC) && cdk synth --parameters TaskMemoryLimit=1024 && cdk deploy --parameters TaskMemoryLimit=1024 --all
