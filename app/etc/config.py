# Funtions to get parameters from AWS SSM Parameter store
# import boto3

# def param_get(param_name):
#     # Create a client for the SSM service
#     ssm = boto3.client('ssm', region_name='us-east-1')

#     # Get the value of the parameter
#     return (ssm.get_parameter(Name=param_name, WithDecryption=True))['Parameter']['Value']
import os
from dotenv import load_dotenv

# Set enviromental variables
load_dotenv()

# Check the environment type, i.e. stage (DEV/TEST/PROD)
env = os.getenv("STAGE")

# Define DB path and credentials from enviromental variables depending on the stage
match env:
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
            "username": os.getenv("USERNAME"),
            "pass": os.getenv("PASS"),
            "host": os.getenv("HOST"),
            "db": "project-tc",
        }
    case "PROD":
        db_config = {
            "type": "mysql+mysqldb",
            "username": os.getenv("USERNAME"),
            "pass": os.getenv("PASS"),
            "host": os.getenv("HOST"),
            "db": "project-tc",
        }
