IMAGE_NAME?=modern-devops:latest

build:
	docker build -t $(IMAGE_NAME) .

run: build
	docker run --name $(shell uuidgen) -d $(IMAGE_NAME) 