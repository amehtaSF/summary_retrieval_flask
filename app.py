

from flask import Flask, request
import boto3
import json
import dotenv
import os

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

table = dynamodb.Table('micronarrative_bot')

app = Flask(__name__)

def get_summary(prolific_id):
    response = table.get_item(Key={'prolific_id': prolific_id})
    item = response.get('Item')
    if item and 'final_scenario' in item:
        summary = item['final_scenario']
    else:
        summary = 'SUMMARY NOT FOUND'
    return summary

def get_all_entries():
    response = table.scan()
    items = response.get('Items')
    return items


@app.route('/api/summary', methods=['POST'])
def api_get_summary():
    if request.headers.get('FLASK-API-KEY') != flask_api_key:
        return "Unauthorized", 401
    prolific_id = request.json.get('prolific_id')
    summary = get_summary(prolific_id)
    payload = {
        'summary': summary
    }
    return payload


@app.route('/api/get_all', methods=['POST', 'GET'])
def api_get_all():
    if request.headers.get('FLASK-API-KEY') != flask_api_key:
        return "Unauthorized", 401
    
    payload = get_all_entries()
    # payload = f"<pre>{json.dumps(payload, indent=2)}</pre>"
    return payload


@app.route('/')
def home():
    return "hello"

if __name__ == '__main__':
    app.run(debug=False)
