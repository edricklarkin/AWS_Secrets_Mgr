# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 09:26:44 2024

Example process to use AWS Secrets Manager via roles anywhere to retreive secrets
Does not require aws_signing_helper application

"""

import json
from dotenv import dotenv_values
from iam_rolesanywhere_session import IAMRolesAnywhereSession

#call .env file with non-sensitive AWS details
env_val = dotenv_values(".env")

#secret id to retreive
secret_id = 'test-secret'

roles_anywhere_session = IAMRolesAnywhereSession(
    profile_arn=env_val.get('PROFILE_ARN'),
    role_arn=env_val.get('ROLE_ARN'),
    trust_anchor_arn=env_val.get('TRUST_ANCHOR_ARN'),
    certificate=env_val.get('CERT_PATH'),
    private_key=env_val.get('PRIVATE_KEY_PATH'),
    region='us-east-1',
).get_session()

client = roles_anywhere_session.client('secretsmanager')

#client returns a dict of strings
secret_string = client.get_secret_value(SecretId=secret_id)['SecretString']

secret_dict = json.loads(secret_string)

user_name = secret_dict['username']
password = secret_dict['password']

print(f'Username is {user_name} and password is {password}.')
