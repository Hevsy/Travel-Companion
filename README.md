# Travel Companion
**Final Project for CS50x Course**

*A web app for storing travel plans and activities*


The first decision to be made - Flask or Django?
Flask is already familiar from PSet9 and is rather straightforward.
Django seems to be a more powerful framework, however, takes significant time to learn. Therefore, I start with Flask.
I selected MySQL as the backend database engine. It took a bit of time to familiarise with SQLAlchemy and make it work properly.
I also introduced unit testing (/test) and simple github actions (.github/workflows) to introduce common DevOps & CI/CD practices.
The idea is to run the app on AWS, so I also took time to study Cloudformation (/cloudformation) and Terraform (/terraform) to us them as Infrastructure as Code tools. Templates evelove with the project, so cloud infrastructure on AWS (VPC, EC2, RDS) can be created automatically. Infrastructure-wise, next step will be to containerise the app. Potentially, I may look into converting the app into serverless configuration with S3, Lambda, SNS or SQS, API Gateway and, probably, convert database to DynamoDB (NoSQL serverless database)
To help shifting between single-machine development and tests/production in the cloud, I put all DB configuration in the external files. The database connection config is stored in etc/config.py and db initialisation script resides in db_init.py.
To have a cleaner main body, I'll put as much functions/objects separately in functions.py and import them to main, where practical.

Recources used:
/vendor/jquery






