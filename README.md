# AWS-Script-Toolkit
Collection of useful scripts for everyday AWS users

### clean_and_delete_buckets.py
This Python script lists all Amazon S3 buckets in an AWS account and allows the user to select one for deletion. After selecting a bucket, the script deletes all objects and versions within the bucket in batches of up to 1000 objects, displaying a progress bar for each file deleted. Once all objects are removed, the script deletes the bucket itself. It also checks for any deny policies on the bucket before proceeding, ensuring that the user has the necessary permissions to perform deletions. This helps streamline the process of fully cleaning and removing S3 buckets and their contents.

### CloudWatch-Log-Eliminator.py
Automates the management of AWS CloudWatch Log Groups by listing all log groups along with their retention policies and providing a streamlined way to enforce retention settings. It fetches all log groups using the AWS SDK (boto3), displays the first ten with abbreviated names for clarity, and summarizes the retention policies across all log groups. Users can easily update log groups that are set to never expire by applying a one-week retention policy through an intuitive interactive menu. This tool enhances log management efficiency, ensures compliance with data retention policies, and helps reduce storage costs by systematically controlling log data lifecycle.

### clean-ami-and-snapshots.py
This Python script is designed to delete EC2 snapshots and AMIs that are older than a specified number of days (90 days by default). It retrieves all snapshots for a given AWS account, compares their creation date to the current date, and deletes any snapshot older than 90 days. If a snapshot belongs to an AMI, it first deregisters the associated AMI before deleting the snapshot. The script helps automate the cleanup of old snapshots and AMIs, ensuring efficient use of storage resources and reducing costs by managing obsolete backups. You need to customize the account ID, date ranges, and AWS region before use.

### tag-ebs-volumes.py
Automates the process of tagging all EBS volumes in a specified AWS region with a custom key-value pair. It connects to AWS EC2, retrieves all volumes in the specified region (default is "us-east-1"), and adds a tag to each volume using the provided key ("backup") and value ("yes"). The script can be easily modified to apply different key-value pairs or to run in different AWS regions. It helps in organizing and managing EBS volumes by ensuring consistent tagging, which can be useful for cost tracking, backups, or automation workflows.

### get-underutilized-resoureces.py
Connects to AWS Trusted Advisor to pull and refresh various cost optimization checks for underutilized or idle AWS resources such as EC2 instances, RDS databases, EBS volumes, Elastic IPs, and more. It lists flagged resources for each check, along with relevant metadata such as region, resource ID, and estimated savings, enabling cost optimization by identifying underutilized assets. The script supports checks for multiple resource types and prints flagged instances along with savings estimates and account details. This helps users quickly identify cost-saving opportunities and optimize resource usage across their AWS account.

## Automated EC2 and EBS Snapshots (relevant before the AWS Backup Service)

### Clean-AMIs-with-Backup-Tag
This AWS Lambda function automates the cleanup of outdated Amazon Machine Images (AMIs) and their associated snapshots for EC2 instances tagged with 'backup'. It scans for such instances, identifies their AMIs based on a naming convention ('Lambda - instanceID'), and checks if they are scheduled for deletion via a 'DeleteOn' tag. Before deleting, it confirms that a new backup has been successfully created on the current day to ensure data safety. This process helps maintain recent backups, reduces storage costs, and automates backup lifecycle management with minimal manual intervention. 

### EC2-Scheduled-AMI-Generation-Lambda
This Python script automates the creation and management of Amazon Machine Images (AMIs) for EC2 instances tagged with 'backup' or 'Backup'. It filters instances based on tags, creates AMIs for each instance, and applies retention policies, either from instance tags or defaulting to 7 days. The created AMIs are tagged with a 'DeleteOn' date, ensuring automatic cleanup after the retention period. This process helps in automating backups and managing AMI lifecycles, making it efficient to maintain up-to-date instance backups while optimizing storage costs.
