# AWS-Script-Toolkit
Collection of useful scripts for everyday AWS users

### clean_and_delete_buckets.py
This Python script lists all Amazon S3 buckets in an AWS account and allows the user to select one for deletion. After selecting a bucket, the script deletes all objects and versions within the bucket in batches of up to 1000 objects, displaying a progress bar for each file deleted. Once all objects are removed, the script deletes the bucket itself. It also checks for any deny policies on the bucket before proceeding, ensuring that the user has the necessary permissions to perform deletions. This helps streamline the process of fully cleaning and removing S3 buckets and their contents.

### CloudWatch-Log-Eliminator.py
Automates the management of AWS CloudWatch Log Groups by listing all log groups along with their retention policies and providing a streamlined way to enforce retention settings. It fetches all log groups using the AWS SDK (boto3), displays the first ten with abbreviated names for clarity, and summarizes the retention policies across all log groups. Users can easily update log groups that are set to never expire by applying a one-week retention policy through an intuitive interactive menu. This tool enhances log management efficiency, ensures compliance with data retention policies, and helps reduce storage costs by systematically controlling log data lifecycle.

### clean-ami-and-snapshots.py
This Python script is designed to delete EC2 snapshots and AMIs that are older than a specified number of days (90 days by default). It retrieves all snapshots for a given AWS account, compares their creation date to the current date, and deletes any snapshot older than 90 days. If a snapshot belongs to an AMI, it first deregisters the associated AMI before deleting the snapshot. The script helps automate the cleanup of old snapshots and AMIs, ensuring efficient use of storage resources and reducing costs by managing obsolete backups. You need to customize the account ID, date ranges, and AWS region before use.

### cognito_user_pool_cleaner.py
This Python script provides a streamlined solution for managing and deleting Amazon Cognito User Pools. It lists all user pools in your AWS account with details including name, ID, creation date, and user count. The script allows you to select multiple user pools by number for deletion without confirmation prompts, even if they contain users. It automatically handles dependencies like custom domains by deleting them first, then proceeds with user pool deletion. The script uses your default AWS region from your AWS CLI configuration, shows real-time deletion status, and continues processing other selections if one deletion fails. This tool is particularly useful for cleaning up test environments or removing unused authentication resources.

### tag-ebs-volumes.py
Automates the process of tagging all EBS volumes in a specified AWS region with a custom key-value pair. It connects to AWS EC2, retrieves all volumes in the specified region (default is "us-east-1"), and adds a tag to each volume using the provided key ("backup") and value ("yes"). The script can be easily modified to apply different key-value pairs or to run in different AWS regions. It helps in organizing and managing EBS volumes by ensuring consistent tagging, which can be useful for cost tracking, backups, or automation workflows.

### get-underutilized-resources.py
Connects to AWS Trusted Advisor to pull and refresh various cost optimization checks for underutilized or idle AWS resources such as EC2 instances, RDS databases, EBS volumes, Elastic IPs, and more. It lists flagged resources for each check, along with relevant metadata such as region, resource ID, and estimated savings, enabling cost optimization by identifying underutilized assets. The script supports checks for multiple resource types and prints flagged instances along with savings estimates and account details. This helps users quickly identify cost-saving opportunities and optimize resource usage across their AWS account.

### preSignedURL-generator.py
This Python script generates pre-signed URLs for objects stored in Amazon S3 buckets. It allows users to select one or more S3 buckets, specify an expiration time for the pre-signed URLs, and generates HTML and text files containing the download links for the objects in the selected buckets. The script provides options for creating combined reports for multiple buckets or separate reports for each bucket. This tool is useful for securely sharing S3 objects with time-limited access.

### opensearch_resource_cleaner.py
This Python script provides a comprehensive solution for managing and cleaning up AWS OpenSearch resources. It offers a streamlined interface that lists all OpenSearch resources in a single view with sequential numbering and allows you to delete multiple resources in one operation. The script handles domains, serverless collections, VPC endpoints, data access policies, network policies, and encryption policies. It automatically uses your default AWS region from your AWS CLI configuration, shows real-time deletion status, and reports any errors immediately as they occur. This tool helps streamline the process of cleaning up OpenSearch resources, ensuring efficient management and cost optimization of your OpenSearch deployments.

### q_business_cleaner.py
This Python script helps manage Amazon Q Business resources by providing a consolidated view of all resources and allowing batch deletion. It lists applications, data sources, indexes, web experiences, plugins, and retrievers with sequential numbering for easy selection. The script handles the proper deletion order and dependencies between resources, ensuring that child resources are deleted before their parent applications. It uses your default AWS region from your AWS CLI configuration, shows real-time deletion status, and provides detailed error reporting. This tool is particularly useful for cleaning up test environments or removing unused Q Business resources.

## Automated EC2 and EBS Snapshots (relevant before the AWS Backup Service)

### Clean-AMIs-with-Backup-Tag
This AWS Lambda function automates the cleanup of outdated Amazon Machine Images (AMIs) and their associated snapshots for EC2 instances tagged with 'backup'. It scans for such instances, identifies their AMIs based on a naming convention ('Lambda - instanceID'), and checks if they are scheduled for deletion via a 'DeleteOn' tag. Before deleting, it confirms that a new backup has been successfully created on the current day to ensure data safety. This process helps maintain recent backups, reduces storage costs, and automates backup lifecycle management with minimal manual intervention. 

### EC2-Scheduled-AMI-Generation-Lambda
This Python script automates the creation and management of Amazon Machine Images (AMIs) for EC2 instances tagged with 'backup' or 'Backup'. It filters instances based on tags, creates AMIs for each instance, and applies retention policies, either from instance tags or defaulting to 7 days. The created AMIs are tagged with a 'DeleteOn' date, ensuring automatic cleanup after the retention period. This process helps in automating backups and managing AMI lifecycles, making it efficient to maintain up-to-date instance backups while optimizing storage costs.
