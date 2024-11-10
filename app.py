

from flask import Flask, request, jsonify
import boto3
import json
import dotenv
from boto3.dynamodb.conditions import Key
import os
from functools import wraps

dotenv.load_dotenv()


aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
region_name = os.getenv('AWS_DEFAULT_REGION')
flask_api_key = os.getenv('FLASK_API_KEY')


dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name
)

table = dynamodb.Table('petr_micronarrative_nov2024')

app = Flask(__name__)


def api_key_required(f):
    # auth decorator
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get('FLASK-API-KEY')
        if not key or key != flask_api_key:
            return "Unauthorized", 401
        return f(*args, **kwargs)
    return decorated


@app.route('/api/summary', methods=['POST'])
@api_key_required
def api_get_summary():
    prolific_id = request.json.get('prolific_id')
    summary = get_summary(prolific_id)
    payload = {
        'summary': summary
    }
    return payload


# @app.route('/api/get_all', methods=['POST', 'GET'])
# @api_key_required
# def api_get_all():
#     payload = get_all_entries()
#     # payload = f"<pre>{json.dumps(payload, indent=2)}</pre>"
#     return payload

@app.route('/api/get_pid', methods=['POST', 'GET'])
@api_key_required
def api_get_pid():
    prolific_id = request.json.get('prolific_id')
    response = table.query(
        KeyConditionExpression=Key('chat_id').eq(prolific_id)
    )
    items = response.get('Items')
    return items


@app.route('/')
def home():
    return "hello"


def get_summary(prolific_id):
    response = table.query(
        KeyConditionExpression=Key('chat_id').eq(prolific_id)
    )
    items = response.get('Items')
    if items and 'scenario' in items[-1]: # TODO: not yet handling if there are multiple entries for the same prolific_id
        summary = items[-1]['scenario']
    else:
        summary = 'SUMMARY NOT FOUND'
    return summary

# def get_all_entries():
#     response = table.scan()
#     items = response.get('Items')
#     return items

if __name__ == '__main__':
    app.run(debug=False)
