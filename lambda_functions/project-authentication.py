import boto3
import json

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition', region_name='us-east-1')
dynamodbTableName = 'project'
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
projectTable = dynamodb.Table(dynamodbTableName)

bucketName = '<BUCKET-NAME>'

def lambda_handler(event, context):
    print(event) #debug
    objectKey = event['queryStringParameters']['objectKey']
    image_bytes = s3.get_object(Bucket=bucketName, Key=objectKey)['Body'].read()
    response = rekognition.search_faces_by_image(
        CollectionId='project_person',
        Image={
            'Bytes': image_bytes
        },
    )
    for match in response['FaceMatches']:
        print(match['Face']['FaceId'], match['Face']['Confidence']) #debug

        face = projectTable.get_item(
            Key={
                'rekognitionId': match['Face']['FaceId']
            }
        )
        if 'Item' in face:
            print('Person found: ', face['Item']) #debug
            return buildResponse(200, {
                'Message': 'Success', 
                'firstName': face['Item']['firstName'],
                'lastName': face['Item']['lastName'],
            })
    print('Person not found') #debug
    return buildResponse(403, {
        'Message': 'Person not found',
    })

def buildResponse(statusCode, body=None):
    response = {
        'statusCode': statusCode,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
    if body is not None:
        response['body'] = json.dumps(body)
    return response
