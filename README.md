# Travel Companion

## A web app for storing travel plans and activities

### Built with Flask, SQLALchemy, MySQL, HTML/CSS and JavaScript

Aplication allows users to create notebooks for they travel plans, to store ideas ideas, places of interest and links organised by the destinations 
Application is being designed to run in the containers on AWS Infrasctuture

Repository also contains CI/CD pipeine built with github actions, that perform unit tests of the application and deploys it to a docker container/repository

## AWS services to be used

* Amazon Virtual Private Cloud (VPC) for creating an isolated virtual network for the resources
* Amazon Elastic Container Service (ECS): to run and manage containers.
* Amazon Relational Database Service (RDS): to provision and manage a MySQL database instance.
* Amazon EC2 Container Registry (ECR) for storing Docker images
* Amazon Elastic Load Balancer (ELB) for distributing traffic across containers
* Amazon CloudWatch for monitoring the infrastructure and applications
