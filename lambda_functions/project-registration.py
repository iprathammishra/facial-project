import boto3

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition', region_name='us-east-1')
dynamodbTableName = 'project'
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
projectTable = dynamodb.Table(dynamodbTableName)

def lambda_handler(event, context):
    print(event) #debug
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    try:
        response = index_person_image(bucket, key)
        print(response) #debug
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            faceId = response['FaceRecords'][0]['Face']['FaceId']
            
            # For example: Pratham_Mishra.jpeg
            name = key.split('.')[0].split('_')
            firstName, lastName = name[0], name[1]
            register_person(faceId, firstName, lastName)
        return response
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e

def index_person_image(bucket, key):
    response = rekognition.index_faces(
        Image={
            "S3Object": {
                "Bucket": bucket,
                "Name": key
            }
        },
        CollectionId="project_person" #for lambda function indexing with rekognition/ create this using aws cli
    )
    return response

def register_person(faceId, firstName, lastName):
    projectTable.put_item(
        Item={
            'rekognitionId': faceId,
            'firstName': firstName,
            'lastName': lastName
        }
    )