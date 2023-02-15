# import boto3

# def param_get(param_name):
#     # Create a client for the SSM service
#     ssm = boto3.client('ssm', region_name='us-east-1')

#     # Get the value of the parameter
#     return (ssm.get_parameter(Name=param_name, WithDecryption=True))['Parameter']['Value']


db_config = {
    "db_type" : "postgresql+psycopg2", 
    "db_username" : "postgres", 
    "db_pass" : "postgres"
    "db_host" : "db-finance1.cxhmztea6vcv.us-east-1.rds.amazonaws.com", 
    "db_file" :"finance"
}

API_KEY = param_get('finance_api-key')
# print (API_KEY, db_config)

db_config_test = {
    "db_type" : "sqlite", 
    "db_username" : None, 
    "db_pass" : None, 
    "db_host" : None, 
    "db_file" :"finance.db"
}
