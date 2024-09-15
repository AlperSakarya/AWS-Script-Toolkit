# Script intended to add tags to volumes with given region and key/value pair
# Make sure the region is correct and modify key/value as you wish

import boto3
region = "us-east-1"
key = "backup"
value = "yes"


client = boto3.client('ec2',region_name=region)
response = client.describe_volumes()
volumes = response['Volumes']

for a_volume in volumes:
	volume_id = a_volume['VolumeId']
	try:
		create_tags = response = client.create_tags(
	    DryRun=False,
	    Resources=[
	        str(volume_id),
	    ],
	    Tags=[
	        {
	            'Key': key,
	            'Value': value
	        },
	    ]
	)
		print("Tag added on to: " + volume_id)
	except Exception as e:
		print(e)
