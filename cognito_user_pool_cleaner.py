#!/usr/bin/env python3
# Cognito User Pool and Identity Pool Cleaner
# This script lists and deletes AWS Cognito User Pools and Identity Pools without confirmation prompts

import boto3
import sys
import time
from botocore.exceptions import ClientError
from datetime import datetime

class CognitoResourceCleaner:
    def __init__(self):
        # Use the default region from AWS CLI configuration
        session = boto3.session.Session()
        self.region = session.region_name or "us-east-1"
        self.cognito_idp_client = boto3.client('cognito-idp', region_name=self.region)
        self.cognito_identity_client = boto3.client('cognito-identity', region_name=self.region)
        
    def print_header(self):
        """Print a header for the application"""
        print("\n" + "=" * 60)
        print("Cognito Resource Cleaner".center(60))
        print("=" * 60)
        print(f"Region: {self.region}")
        print("=" * 60 + "\n")

    def fetch_user_pools(self):
        """Fetch all Cognito User Pools and return them in a list"""
        user_pools = []
        resource_index = 1  # Start numbering from 1
        
        print("Fetching Cognito User Pools...")
        try:
            paginator = self.cognito_idp_client.get_paginator('list_user_pools')
            for page in paginator.paginate(MaxResults=60):
                for pool in page.get('UserPools', []):
                    # Get detailed information about the user pool
                    try:
                        details = self.cognito_idp_client.describe_user_pool(
                            UserPoolId=pool['Id']
                        )
                        user_count = details['UserPool'].get('EstimatedNumberOfUsers', 0)
                    except ClientError as e:
                        print(f"Error getting details for user pool {pool['Id']}: {e}")
                        user_count = "Unknown"
                    
                    user_pools.append({
                        'index': resource_index,
                        'name': pool['Name'],
                        'id': pool['Id'],
                        'creation_date': pool['CreationDate'].strftime('%Y-%m-%d %H:%M:%S'),
                        'user_count': user_count,
                        'type': 'User Pool'
                    })
                    resource_index += 1
        except ClientError as e:
            print(f"Error listing user pools: {e}")
        
        return user_pools, resource_index

    def fetch_identity_pools(self, start_index):
        """Fetch all Cognito Identity Pools and return them in a list"""
        identity_pools = []
        resource_index = start_index  # Continue numbering from where user pools left off
        
        print("Fetching Cognito Identity Pools...")
        try:
            paginator = self.cognito_identity_client.get_paginator('list_identity_pools')
            for page in paginator.paginate(MaxResults=60):
                for pool in page.get('IdentityPools', []):
                    identity_pools.append({
                        'index': resource_index,
                        'name': pool['IdentityPoolName'],
                        'id': pool['IdentityPoolId'],
                        'creation_date': 'N/A',  # Identity pools don't expose creation date in list API
                        'user_count': 'N/A',     # Identity pools don't have a user count concept
                        'type': 'Identity Pool'
                    })
                    resource_index += 1
        except ClientError as e:
            print(f"Error listing identity pools: {e}")
        
        return identity_pools

    def display_resources(self, resources):
        """Display all resources in a consolidated view"""
        if not resources:
            print("No Cognito resources found.")
            return
        
        print("\nAvailable Cognito Resources:")
        print("-" * 110)
        print(f"{'#':<5} {'Type':<15} {'Name':<30} {'ID':<30} {'Creation Date':<20} {'Users':<10}")
        print("-" * 110)
        
        for resource in resources:
            print(f"{resource['index']:<5} {resource['type']:<15} {resource['name']:<30} {resource['id']:<30} {resource['creation_date']:<20} {resource['user_count']:<10}")
    
    def select_resources(self, resources):
        """Let user select resources by number"""
        if not resources:
            return []
        
        selection = input("\nEnter the number(s) of resources to delete (comma-separated): ")
        
        selected_indices = []
        try:
            for num in selection.split(','):
                num = num.strip()
                if num:  # Skip empty strings
                    selected_indices.append(int(num))
        except ValueError:
            print(f"Invalid input: {num}. Must be a number.")
            return []
        
        selected_resources = []
        for resource in resources:
            if resource['index'] in selected_indices:
                selected_resources.append(resource)
        
        if not selected_resources:
            print("No valid resources selected.")
        else:
            print(f"\nSelected {len(selected_resources)} resources for deletion:")
            for resource in selected_resources:
                users = resource['user_count'] if resource['type'] == 'User Pool' else 'N/A'
                print(f"  {resource['index']}. {resource['type']} - {resource['name']} ({resource['id']}) - Users: {users}")
        
        return selected_resources

    def delete_resources(self, resources):
        """Delete selected resources without confirmation"""
        print("\nDeleting resources...")
        
        for resource in resources:
            if resource['type'] == 'User Pool':
                self.delete_user_pool(resource)
            elif resource['type'] == 'Identity Pool':
                self.delete_identity_pool(resource)
    
    def delete_user_pool(self, pool):
        """Delete a Cognito User Pool"""
        print(f"\nDeleting User Pool: {pool['name']} ({pool['id']})...")
        
        # First check if the user pool has a domain configured
        try:
            domain_response = self.cognito_idp_client.describe_user_pool(
                UserPoolId=pool['id']
            )
            
            # Check if the user pool has a domain
            if 'Domain' in domain_response['UserPool']:
                domain = domain_response['UserPool']['Domain']
                print(f"User pool has a domain configured: {domain}. Deleting domain first...")
                
                try:
                    self.cognito_idp_client.delete_user_pool_domain(
                        Domain=domain,
                        UserPoolId=pool['id']
                    )
                    print(f"Domain {domain} deleted successfully.")
                    
                    # Wait a moment for the domain deletion to propagate
                    time.sleep(5)
                except ClientError as domain_error:
                    print(f"ERROR: Failed to delete domain {domain}: {domain_error}")
                    return  # Skip this user pool if domain deletion fails
        except ClientError as e:
            print(f"ERROR: Failed to check domain for User Pool {pool['name']} ({pool['id']}): {e}")
            return  # Skip this user pool if we can't check for domains
        
        # Now delete the user pool
        try:
            # Delete the user pool without confirmation
            self.cognito_idp_client.delete_user_pool(
                UserPoolId=pool['id']
            )
            print(f"User Pool {pool['name']} ({pool['id']}) deletion initiated.")
            
            # Wait for deletion to complete
            self._wait_for_user_pool_deletion(pool['id'])
        except ClientError as e:
            print(f"ERROR: Failed to delete User Pool {pool['name']} ({pool['id']}): {e}")

    def delete_identity_pool(self, pool):
        """Delete a Cognito Identity Pool"""
        print(f"\nDeleting Identity Pool: {pool['name']} ({pool['id']})...")
        try:
            # Delete the identity pool without confirmation
            self.cognito_identity_client.delete_identity_pool(
                IdentityPoolId=pool['id']
            )
            print(f"Identity Pool {pool['name']} ({pool['id']}) deleted successfully.")
        except ClientError as e:
            print(f"ERROR: Failed to delete Identity Pool {pool['name']} ({pool['id']}): {e}")
    
    def _wait_for_user_pool_deletion(self, user_pool_id):
        """Wait for a user pool to be deleted"""
        print(f"Waiting for user pool deletion to complete...")
        max_attempts = 30
        attempts = 0
        
        while attempts < max_attempts:
            try:
                self.cognito_idp_client.describe_user_pool(UserPoolId=user_pool_id)
                print("Still deleting...")
                time.sleep(2)  # Check every 2 seconds
                attempts += 1
            except ClientError as e:
                if 'ResourceNotFoundException' in str(e) or 'UserPoolNotFoundException' in str(e):
                    print(f"User Pool {user_pool_id} successfully deleted.")
                    return
                else:
                    print(f"Error checking user pool status: {str(e)}")
                    return
        
        print(f"Deletion of User Pool {user_pool_id} is taking longer than expected. It may still be in progress.")

    def run(self):
        """Main execution flow"""
        self.print_header()
        
        # Fetch all resources
        user_pools, next_index = self.fetch_user_pools()
        identity_pools = self.fetch_identity_pools(next_index)
        
        # Combine all resources
        all_resources = user_pools + identity_pools
        
        # Display all resources
        self.display_resources(all_resources)
        
        # Let user select resources to delete
        selected_resources = self.select_resources(all_resources)
        
        # Delete selected resources without confirmation
        if selected_resources:
            self.delete_resources(selected_resources)
        
        print("\nOperation completed.")

if __name__ == "__main__":
    cleaner = CognitoResourceCleaner()
    cleaner.run()
