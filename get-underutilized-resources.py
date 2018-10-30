# Script intended to pull idle TA resources for a given account
# Refreshes and displays flagged resources for "Cost Optimization" category here https://aws.amazon.com/premiumsupport/ta-iam/
# Need to implement multi-account and aggregated list options

import boto3

client = boto3.client('support')
iam = boto3.resource('iam')
iam2 = boto3.client('iam')
account_id = iam.CurrentUser().arn.split(':')[4]
account_alias = iam2.list_account_aliases()['AccountAliases'][0]

language = "en"

# Cost Optimization Checks
# You can get more check IDs from here https://aws.amazon.com/premiumsupport/ta-iam/
# and add them to the below array like this ta_checks = ['Qch7DwouX1', 'new_check1', 'new_check2']
ta_checks = {"Qch7DwouX1" : "Low Utilization Amazon EC2 Instances",
			 "Ti39halfu8" : "Amazon RDS Idle DB Instances",
			 "DAvU99Dc4C" : "Underutilized Amazon EBS Volumes",
			 "G31sQ1E9U"  : "Underutilized Amazon Redshift Clusters",
			 "hjLMh88uM8" : "Idle Load Balancers",
			 "Z4AUBRNSmz" : "Unassociated Elastic IP Addresses",
			 "1e93e4c0b5" : "Amazon EC2 Reserved Instance Lease Expiration",
			 "1MoPEMsKx6" : "Amazon EC2 Reserved Instances Optimization"}


# Refresh the checks first
def refresh_checks():
	for a_check in ta_checks:
		try:
			response = client.refresh_trusted_advisor_check(checkId=a_check)
			if response['ResponseMetadata']['HTTPStatusCode'] == 200:
				print("Refreshed TA checks for: " + str(a_check)) 
			else:
				print("check: " + a_check + "could not be refreshed")
		except Exception as e:
			print(e)


def get_ec2_check_results():
	check_id = "Qch7DwouX1"
	try:
		response = client.describe_trusted_advisor_check_result(checkId=check_id, language=language)
		flagged_resources = response['result']['flaggedResources']
		estimated_savings = response['result']['categorySpecificSummary']['costOptimizing']['estimatedMonthlySavings']
		instance = response['result']['flaggedResources'][0]['metadata']

		if response['ResponseMetadata']['HTTPStatusCode'] == 200:
			if not flagged_resources:
				print("====> No Low Utilization RDS Instances Found!")
			else:				
				for an_instance in flagged_resources:
					print("=== Low Utilization Amazon EC2 Instances ===")
					print("Account ID: " + account_id + "| Account Name: " + account_alias)
					print("Region: " + str(instance[0]) + " | " + "Instance ID: " + str(instance[1]) 
						+ " | " + "Instance Type: " + str(instance[3] + " | " + "Estimated Savings: " + str(instance[4])))
		else:
			print("error")
	except Exception as e:
		print(e)


def get_rds_check_results():
	check_id = "Ti39halfu8"
	try:
		response = client.describe_trusted_advisor_check_result(checkId=check_id, language=language)
		flagged_resources = response['result']['flaggedResources']
		#instance = response['result']['flaggedResources'][0]['metadata']

		if response['ResponseMetadata']['HTTPStatusCode'] == 200:
			if not flagged_resources:
				print("====> No Low Utilization RDS Instances Found!")
			else:
				print(flagged_resources)	
				for an_instance in flagged_resources:
					print("=== Low Utilization Amazon RDS Instances ===")
					print("Account ID: " + account_id + "| Account Name: " + account_alias)
					print(an_instance)
		else:
			print("error")

	except Exception as e:
		print(e)


def get_ebs_check_results():
	check_id = "DAvU99Dc4C"
	try:
		response = client.describe_trusted_advisor_check_result(checkId=check_id, language=language)
		flagged_resources = response['result']['flaggedResources']
		volume = response['result']['flaggedResources'][0]['metadata']

		if response['ResponseMetadata']['HTTPStatusCode'] == 200:
			if not flagged_resources:
				print("====> No Low Utilization EBS Volumes Found!")
			else:	
				for a_volume in flagged_resources:
					print("=== Low Utilization EBS Volumes ===")
					print("Account ID: " + account_id + "| Account Name: " + account_alias)
					print("Region: " + str(volume[0]) + " | " + "Volume ID: " + str(volume[1]) 
						+ " | " + "Volume Type: " + str(volume[3] + " | " + "Estimated Savings: " + str(volume[5])))
		else:
			print("error")
	except Exception as e:
		print(e)


def get_redshift_check_results():
	check_id = "G31sQ1E9U"
	try:
		response = client.describe_trusted_advisor_check_result(checkId=check_id, language=language)
		flagged_resources = response['result']['flaggedResources']
		#cluster = response['result']['flaggedResources'][0]['metadata']

		if response['ResponseMetadata']['HTTPStatusCode'] == 200:
			if not flagged_resources:
				print("====> No Low Utilization Clusters Found!")
			else:	
				for a_cluster in flagged_resources:
					print("=== Low Utilization Clusters ===")
					print("Account ID: " + account_id + "| Account Name: " + account_alias)
					print(a_cluster)	
		else:
			print("error")
	except Exception as e:
		print(e)


def get_elb_check_results():
	check_id = "hjLMh88uM8"
	try:
		response = client.describe_trusted_advisor_check_result(checkId=check_id, language=language)
		flagged_resources = response['result']['flaggedResources']
		#elb = response['result']['flaggedResources'][0]['metadata']

		if response['ResponseMetadata']['HTTPStatusCode'] == 200:
			if not flagged_resources:
				print("====> No Low Utilization ELB Found!")
			else:	
				for an_elb in flagged_resources:
					print("=== Low Utilization ELBs ===")
					print("Account ID: " + account_id + "| Account Name: " + account_alias)
					print(an_elb)	
		else:
			print("error")
	except Exception as e:
		print(e)


def get_eip_check_results():
	check_id = "Z4AUBRNSmz"
	try:
		response = client.describe_trusted_advisor_check_result(checkId=check_id, language=language)
		flagged_resources = response['result']['flaggedResources']
		eip = response['result']['flaggedResources'][0]['metadata']

		if response['ResponseMetadata']['HTTPStatusCode'] == 200:
			if not flagged_resources:
				print("====> No Unassociated Elastic IP Addresses Found!")
			else:	
				for an_elb in flagged_resources:
					print("=== Unassociated Elastic IP Addresses ===")
					print("Account ID: " + account_id + "| Account Name: " + account_alias)
					print("Region: " + str(eip[0]) + " | " + "EIP: " + str(eip[1]))
		else:
			print("error")
	except Exception as e:
		print(e)


def get_ri_expiration_check_results():
	check_id = "1e93e4c0b5"
	try:
		response = client.describe_trusted_advisor_check_result(checkId=check_id, language=language)
		flagged_resources = response['result']['flaggedResources']
		#riexp = response['result']['flaggedResources'][0]['metadata']

		if response['ResponseMetadata']['HTTPStatusCode'] == 200:
			if not flagged_resources:
				print("====> No RI Expiration Found!")
			else:	
				for an_expiration in flagged_resources:
					print("=== RI Expirations ===")
					print("Account ID: " + account_id + "| Account Name: " + account_alias)
					print(an_expiration)	
		else:
			print("error")
	except Exception as e:
		print(e)


def get_ri_optimization_results():
	check_id = "1MoPEMsKx6"
	try:
		response = client.describe_trusted_advisor_check_result(checkId=check_id, language=language)
		flagged_resources = response['result']['flaggedResources']
		#rires = response['result']['flaggedResources'][0]['metadata']

		if response['ResponseMetadata']['HTTPStatusCode'] == 200:
			if not flagged_resources:
				print("====> No RI Optimization Result Found!")
			else:	
				for optimization in flagged_resources:
					print("=== RI Optimization Result ===")
					print("Account ID: " + account_id + "| Account Name: " + account_alias)
					print(optimization)	
		else:
			print("error")
	except Exception as e:
		print(e)


refresh_checks()
get_ec2_check_results()
get_rds_check_results()
get_ebs_check_results()
get_redshift_check_results()
get_elb_check_results()
get_eip_check_results()
get_ri_expiration_check_results()
get_ri_optimization_results()
