# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 10:36:41 2024

Example process for rotating secrets for an on-premises service
Secrets stored to AWS Secrets Manager

NOTE: this example assumes the user has authority to change own password

"""

import random
import string
import MySQLdb
import json
from dotenv import dotenv_values
from iam_rolesanywhere_session import IAMRolesAnywhereSession
from copy import deepcopy

#call .env file with non-sensitive AWS details
env_val = dotenv_values(".env")

#global variables
secret_name = 'test-secret'

#connect to secrets manager
roles_anywhere_session = IAMRolesAnywhereSession(
    profile_arn=env_val.get('PROFILE_ARN'),
    role_arn=env_val.get('ROLE_ARN'),
    trust_anchor_arn=env_val.get('TRUST_ANCHOR_ARN'),
    certificate=env_val.get('CERT_PATH'),
    private_key=env_val.get('PRIVATE_KEY_PATH'),
    region='us-east-1'
    ).get_session()

client = roles_anywhere_session.client('secretsmanager',verify=False)

#create random password
def generate_password(length):
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

#get database credentials from AWS Secrets Manager
def get_db_credentials():
    
    return json.loads(client.get_secret_value(SecretId=secret_name)['SecretString'])
 
#copy current secrets dict and change password in new secret dict
current_secret = get_db_credentials()
new_secret = deepcopy(current_secret)
new_secret['password'] = generate_password(12)


#connect to database
db = MySQLdb.connect(host=current_secret['host'],
                                user=current_secret['username'],
                                passwd=current_secret['password'], 
                                db='mysql')

#execute password change code and close dabase connection 
cur = db.cursor()
cur.execute(f"ALTER USER '{new_secret['username']}'@'%' IDENTIFIED BY '{new_secret['password']}';")
db.close()

#change password in AWS Secret Manager
client.update_secret(SecretId=secret_name, 
                     SecretString=json.dumps(new_secret))


