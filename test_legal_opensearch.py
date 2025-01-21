import boto3
import json
import requests
from requests_aws4auth import AWS4Auth

from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
import sys

client = boto3.client('bedrock',region_name='us-east-1')
bedrock_runtime = boto3.client('bedrock-runtime',region_name='us-east-1')

region = 'us-east-1' # For example, us-west-1
service = 'es'
credentials = boto3.Session().get_credentials()
print("*****start***********")
print(region)
print("*******end*********")
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)


def main2(prompt):

    # if len(sys.argv) < 2:
    #     print("Please provide input text as command line argument")
    #     sys.exit(1)
    # input_text = sys.argv[1]
    input_text = prompt
    # Build our request to Bedrock to generate a Opensearch Query from natural language
    payload = {
        "modelId": "us.anthropic.claude-3-haiku-20240307-v1:0", 
        "contentType": "application/json",
        "accept": "application/json",
        "body": {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "system": "Act as a Opensearch DQL writer that can generate queries based on the user's natural language input. Generate an Opensearch DQL query as JSON that can be queried on an index containing company name and breach notification and agreement date. The fields available are 'company', 'AMAZON_BEDROCK_TEXT\' and 'breach_notification_required'. Return only JSON and nothing more.",
            "messages": [
                {
                    "role": "user", 
                    "content": [
                        {
                            "type": "text",
                            "text": "what are the breach notification requirements for each client?"
                        }
                    ]
                },
                {
                    "role": "assistant", 
                    "content": [
                        {
                            "type": "text",
                            "text": "{\"bool\": {\"must\": [{\"term\": {\"breach_notification_required\": true}},{\"exists\": {\"field\": \"company\"}},{\"script\": {\"script\": {\"source\": \"doc['company.keyword'].value.length() > 0\"}}}]}}}"
                        }
                    ]
                },
                {
                    "role": "user", 
                    "content": [
                        {
                            "type": "text",
                            "text": "what are the not breach notification requirements for each client?"
                        }
                    ]
                },
                {
                    "role": "assistant", 
                    "content": [
                        {
                            "type": "text",
                            "text": "{\"bool\": {\"must\": [{\"term\": {\"breach_notification_required\": false}},{\"exists\": {\"field\": \"company\"}},{\"script\": {\"script\": {\"source\": \"doc['company.keyword'].value.length() > 0\"}}}]}}"
                        }
                    ]
                },
                {
                    "role": "user", 
                    "content": [
                        {
                            "type": "text",
                            "text": input_text
                        }
                    ]
                }
            ]
        }
    }

    # Convert the payload to bytes
    body_bytes = json.dumps(payload['body']).encode('utf-8')

    # Invoke the model
    response = bedrock_runtime.invoke_model(
        body = body_bytes,
        contentType = payload['contentType'],
        accept = payload['accept'],
        modelId = payload['modelId'],
    )

    # Print the response
    response_body = response['body'].read().decode('utf-8')
    print(json.dumps(json.loads(response_body), indent=2))

    # Get DQL
    search_query = json.loads(response_body)['content'][0]['text']
    print("Running DQL:", search_query)



    host = 'kye63mm2ijgu494noer4.us-east-1.aoss.amazonaws.com' # cluster endpoint, for example: my-test-domain.us-east-1.aoss.amazonaws.com
    region = 'us-east-1'
    service = 'aoss'
    credentials = boto3.Session().get_credentials()
    auth = AWSV4SignerAuth(credentials, region, service)
    #print("Auth",auth)
    #print("Credentials:",credentials.access_key)

    client = OpenSearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth = auth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection,
        pool_maxsize = 20
    )

    query = {
        'size': 10000,
        "_source": [
                    "company", 
                    "breach_notification_required", 
                    "Agreement_date",
                    # "time_entry_requirements",
                    # "types_of_expenses", 
                    "AMAZON_BEDROCK_TEXT",
                    "x-amz-bedrock-kb-source-uri"],
        'query': json.loads(search_query),
        "aggs": {
            "unique_companies": {
                "terms": {
                    "field": "company.keyword",
                    "size": 10000
                }
            }
        }
    }

    response = client.search(
        body = query,
        index = 'bedrock-knowledge-base-default-index'
    )
    return response

    print(json.dumps(response, indent=2))


if __name__ == "__main__":
    main2()