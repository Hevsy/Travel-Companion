# Funtions to get parameters from AWS SSM Parameter store
# import boto3

# def param_get(param_name):
#     # Create a client for the SSM service
#     ssm = boto3.client('ssm', region_name='us-east-1')

#     # Get the value of the parameter
#     return (ssm.get_parameter(Name=param_name, WithDecryption=True))['Parameter']['Value']


db_config = {
    "type": "mysql+mysqldb",
    "username": "root",
    "pass": "root",
    "host": "localhost",
    "db": "project-tc",
}

db_config_test = {
    "type": "sqlite",
    "username": None,
    "pass": None,
    "host": None,
    "db": "finance.db",
}
