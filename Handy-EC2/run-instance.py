import boto
from boto.ec2.blockdevicemapping import BlockDeviceMapping

ec2 = boto.connect_ec2()

AMI_ID = "ami-8fcee4e5"
EC2_KEY_HANDLE = "EC2-NEW"
INSTANCE_TYPE = "t2.micro"
SEC_GROUP_HANDLE = "default"

dev_sda1 = boto.ec2.blockdevicemapping.EBSBlockDeviceType()
dev_sda1.size = 50
dev_sda1.volume_type = 'gp2'
bdm = boto.ec2.blockdevicemapping.BlockDeviceMapping()
bdm['/dev/xvda'] = dev_sda1

reservation = ec2.run_instances(image_id=AMI_ID,
                                 instance_type=INSTANCE_TYPE,
                                 security_groups=[SEC_GROUP_HANDLE],
                                 key_name=EC2_KEY_HANDLE,
                                 block_device_map=bdm
                                )