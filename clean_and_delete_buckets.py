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

# Get bucket(s) to delete (allows multiple numbers)
bucket_numbers_to_delete = input("Enter the number(s) of the bucket(s) to delete (comma-separated): ").split(',')

# Validate and convert input to bucket names
buckets_to_delete = []
for num in bucket_numbers_to_delete:
    try:
        bucket_name = response['Buckets'][int(num.strip())]['Name']
        buckets_to_delete.append(bucket_name)
    except (ValueError, IndexError):
        print(f"Invalid bucket number: {num}. Skipping.")

if not buckets_to_delete:
    print("No valid buckets selected. Exiting.")
    exit()

for bucket_to_delete in buckets_to_delete:
    try:
        print(f"\nDeleting bucket: {bucket_to_delete}")

        # Delete all object versions (including delete markers) from the bucket
        deleting = True
        while deleting:
            version_objs = s3.list_object_versions(Bucket=bucket_to_delete)
            if 'Versions' in version_objs or 'DeleteMarkers' in version_objs:
                objects_to_delete = []

                if 'Versions' in version_objs:
                    objects_to_delete.extend(
                        [{'Key': obj['Key'], 'VersionId': obj['VersionId']} for obj in version_objs['Versions']]
                    )

                if 'DeleteMarkers' in version_objs:
                    objects_to_delete.extend(
                        [{'Key': obj['Key'], 'VersionId': obj['VersionId']} for obj in version_objs['DeleteMarkers']]
                    )

                if objects_to_delete:
                    delete_keys = {'Objects': objects_to_delete}
                    s3.delete_objects(Bucket=bucket_to_delete, Delete=delete_keys)
                    print(f"Deleted {len(objects_to_delete)} object versions and delete markers from {bucket_to_delete}")
            else:
                deleting = False
                print(f"No more object versions or delete markers in {bucket_to_delete}")

        # Now delete the bucket
        s3.delete_bucket(Bucket=bucket_to_delete)
        print(f"Deleted bucket {bucket_to_delete}")

    except ClientError as e:
        print(f"Error deleting bucket {bucket_to_delete}: {e}")
