# Script intended to delete snapshots and AMIs that are older than certain date
# You need to replace YOUR_ACCOUNT_ID with your account ID :)
# You need to change min and max dates in line 20 and 23

import boto3
import datetime
import time
client = boto3.client('ec2',region_name='us-east-1')
snapshots = client.describe_snapshots(OwnerIds=['YOUR_ACCOUNT_ID'])

if snapshots['Snapshots']:

	for snapshot in snapshots['Snapshots']:
		a=snapshot['StartTime']
		b=a.date()
		c=datetime.datetime.now().date()
		d=c-b
		try:
			snapid = snapshot['SnapshotId']
			if d.days >= 90:
				client.delete_snapshot(SnapshotId=snapid)
				print (snapid + " DELETED")
			elif d.days < 10:
				print ("SKIPPED " + str(snapid))

		except Exception as e:
			if 'InvalidSnapshot.InUse' in str(e):
				ami_id = str(e)
				clean_ami_id = ami_id.split()[17]
				print ("This snapshot: " + snapid + " belogs to an AMI - De-Registering the AMI: " + clean_ami_id + " first..." )
				try:
					client.deregister_image(ImageId=clean_ami_id)
				except Exception as AMI_Deregister_Error:
					print (AMI_Deregister_Error)
				time.sleep(1)
				client.delete_snapshot(SnapshotId=snapid)
				print (snapid + " DELETED")
			else:
				print(e)
		continue
else:
  print ("No snapshot found!")
