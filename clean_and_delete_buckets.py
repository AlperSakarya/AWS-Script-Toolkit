# Script intended to list all buckets and let you select a number.
# Issues a delete for all objects and all versions.
# Displays a horizontal bar for everfile it's deleting.


import boto3
from botocore.exceptions import ClientError  
from tqdm import tqdm

s3 = boto3.client('s3')

# List buckets
response = s3.list_buckets()

print("Existing S3 Buckets:")  
for i, bucket in enumerate(response['Buckets']):
  print(f"{i}. {bucket['Name']}")
  
# Get bucket to delete
bucket_to_delete = input("Enter the number of the bucket to delete: ")
bucket_to_delete = response['Buckets'][int(bucket_to_delete)]['Name']   

try:
  # Check for Deny policy
  policy = s3.get_bucket_policy(Bucket=bucket_to_delete)
  if policy['Policy'].find('Deny') != -1:
    print(f"Bucket {bucket_to_delete} has a Deny policy, quitting.")
    exit()

except ClientError as e:
  if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
    print(f"Bucket {bucket_to_delete} has no policy set.")
  else:
    raise

confirm = input(f"Confirm delete bucket {bucket_to_delete} (y/n): ")
if confirm.lower() == 'y':

  deleting = True
  
  while deleting:

    objs = s3.list_objects_v2(Bucket=bucket_to_delete, MaxKeys=1000)
    
    if 'Contents' in objs and len(objs['Contents']) >= 1000:
      print("Found more than 1000 objects, making a batch delete request for 1000 objects...")
      delete_keys = {'Objects': [{'Key': obj['Key']} for obj in objs['Contents']]}
      s3.delete_objects(Bucket=bucket_to_delete, Delete=delete_keys)

    elif 'Contents' in objs:
      print("Less than 1000 objects, deleting individually")  
      files = [obj['Key'] for obj in objs['Contents']]
        
      with tqdm(total=len(files)) as pbar:
        for file in files:
          s3.delete_object(Bucket=bucket_to_delete, Key=file)
          pbar.update(1)
          pbar.set_description(f"Deleting {file}")

    else:
      deleting = False
      print("No objects left to delete")
      
  s3.delete_bucket(Bucket=bucket_to_delete)

  print(f"Deleted bucket {bucket_to_delete}")
  
else:
  print("Delete canceled")