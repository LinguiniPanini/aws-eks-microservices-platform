import json
import os
import boto3

_cache = {}
_client = boto3.client('secretsmanager', region_name=os.environ.get('AWS_REGION', 'us-east-1'))

def get(name):
    if name not in _cache:
        resp = _client.get_secret_value(SecretId=name)
        value = resp['SecretString']
        try:
            _cache[name] = json.loads(value)
        except (ValueError, TypeError):
            _cache[name] = value
    return _cache[name]
