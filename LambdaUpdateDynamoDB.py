def check_license_key(ec2InstanceId, eventAccountId):
  awsRegion = 'eu-central-1'
  tableName = 'MyDynamoDBTable'
  indexName = 'MyIndexName'
  print(f"Checking if InstanceId {ec2InstanceId} has already a license key")
  client = boto3.client('dynamodb', region_name=awsRegion)
  
  try:
    data = client.query(
      TableName=tableName,
      IndexName=indexName,
      KeyConditionExpression='InstanceID = :id',
      ExpressionAttributeValues={
        ':id': {
          'S': f'{ec2InstanceId}'
        }
      },
    )
    if len(data["Items"]) != 0:
      licenseKey = (data["Items"][0]["LicenseKey"]["S"])
      print(f"Instance {ec2InstanceId} already has a license key assigned: {licenseKey}")
      return licenseKey 
    elif len(data["Items"]) == 0:
      print("Instance has no license key assigned. Starting querying for free license keys...")
      data = client.query(
      TableName=tableName,
      IndexName=indexName,
      KeyConditionExpression='InstanceID = :id',
      ExpressionAttributeValues={
        ':id': {
          'S': 'null'
        }
      },
      Limit=1,
      )
      licenseKey = (data["Items"][0]["LicenseKey"]["S"])
      update_license_key_table(licenseKey, eventAccountId, ec2InstanceId)
      return licenseKey
    else:
      return
  except Exception as e:
    print("Unexpected error has occured on db query!")
    raise(e)

def update_license_key_table(licenseKey, eventAccountId, ec2InstanceId):    
  awsRegion = 'eu-central-1'
  tableName = 'MyDynamoDBTable'
  print(f"Updating DynamoDB table LicenseKey {licenseKey}")
  client = boto3.client('dynamodb', region_name='eu-central-1')
  
  
  try:
    ec2InstanceARN = f"arn:aws:ec2:{awsRegion}:{eventAccountId}:instance/{ec2InstanceId}"
    update_data = client.update_item (
      ExpressionAttributeNames={
      '#ARN': 'EC2InstanceARN',
      '#ID': 'InstanceID',
      },
      ExpressionAttributeValues={
        ':t': {
          'S': ec2InstanceARN,
        },
        ':y': {
          'S': ec2InstanceId,
        },
      },
      Key={
        'LicenseKey': {
          'S': licenseKey
        },
      },
      ReturnValues='ALL_NEW',
      TableName=tableName,
      UpdateExpression='SET #ID = :y, #ARN = :t',
    )
    print("DynamoDB update completed")
  except Exception as e:
    print(f"Failed to update DynamoDB table!")
    raise(e)