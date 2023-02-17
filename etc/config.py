# Funtions to get parameters from AWS SSM Parameter store
# import boto3

# def param_get(param_name):
#     # Create a client for the SSM service
#     ssm = boto3.client('ssm', region_name='us-east-1')

#     # Get the value of the parameter
#     return (ssm.get_parameter(Name=param_name, WithDecryption=True))['Parameter']['Value']


db_config = {
    "db_type": "mysql+mysqlconnector",
    "db_username": "root",
    "db_pass": "root",
    "db_host": "localhost",
    "db_file": "project-tc"
}

db_config_test = {
    "db_type": "sqlite",
    "db_username": None,
    "db_pass": None,
    "db_host": None,
    "db_file": "finance.db"
}
