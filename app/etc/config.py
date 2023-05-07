# Funtions to get parameters from AWS SSM Parameter store
# import boto3

# def param_get(param_name):
#     # Create a client for the SSM service
#     ssm = boto3.client('ssm', region_name='us-east-1')

#     # Get the value of the parameter
#     return (ssm.get_parameter(Name=param_name, WithDecryption=True))['Parameter']['Value']
import os
from dotenv import load_dotenv

load_dotenv()

match os.getenv("STAGE"):
    case "DEV":
        db_config = {
            "type": "sqlite",
            "username": None,
            "pass": None,
            "host": None,
            "db": "project-tc.db",
        }
    case "TEST":
        db_config = {
            "type": "mysql+mysqldb",
            "username": "root",
            "pass": "root",
            "host": "localhost",
            "db": "project-tc",
        }
    case "PROD":
        db_config = {
            "type": "mysql+mysqldb",
            "username": "root",
            "pass": "root",
            "host": "localhost",
            "db": "project-tc",
        }

