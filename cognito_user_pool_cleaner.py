#!/usr/bin/env python3
# Cognito User Pool Cleaner
# This script lists and deletes AWS Cognito User Pools without confirmation prompts

import boto3
import sys
import time
from botocore.exceptions import ClientError
from datetime import datetime

class CognitoUserPoolCleaner:
    def __init__(self):
        # Use the default region from AWS CLI configuration
        session = boto3.session.Session()
        self.region = session.region_name or "us-east-1"
        self.cognito_client = boto3.client('cognito-idp', region_name=self.region)
        
    def print_header(self):
        """Print a header for the application"""
        print("\n" + "=" * 60)
        print("Cognito User Pool Cleaner".center(60))
        print("=" * 60)
        print(f"Region: {self.region}")
        print("=" * 60 + "\n")

    def fetch_user_pools(self):
        """Fetch all Cognito User Pools and return them in a list"""
        user_pools = []
        resource_index = 1  # Start numbering from 1
        
        print("Fetching Cognito User Pools...")
        try:
            paginator = self.cognito_client.get_paginator('list_user_pools')
            for page in paginator.paginate(MaxResults=60):
                for pool in page.get('UserPools', []):
                    # Get detailed information about the user pool
                    try:
                        details = self.cognito_client.describe_user_pool(
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
                        'user_count': user_count
                    })
                    resource_index += 1
        except ClientError as e:
            print(f"Error listing user pools: {e}")
        
        return user_pools

    def display_user_pools(self, user_pools):
        """Display all user pools in a consolidated view"""
        if not user_pools:
            print("No Cognito User Pools found.")
            return
        
        print("\nAvailable Cognito User Pools:")
        print("-" * 100)
        print(f"{'#':<5} {'Name':<30} {'ID':<30} {'Creation Date':<20} {'Users':<10}")
        print("-" * 100)
        
        for pool in user_pools:
            print(f"{pool['index']:<5} {pool['name']:<30} {pool['id']:<30} {pool['creation_date']:<20} {pool['user_count']:<10}")
    
    def select_user_pools(self, user_pools):
        """Let user select user pools by number"""
        if not user_pools:
            return []
        
        selection = input("\nEnter the number(s) of user pools to delete (comma-separated): ")
        
        selected_indices = []
        try:
            for num in selection.split(','):
                num = num.strip()
                if num:  # Skip empty strings
                    selected_indices.append(int(num))
        except ValueError:
            print(f"Invalid input: {num}. Must be a number.")
            return []
        
        selected_pools = []
        for pool in user_pools:
            if pool['index'] in selected_indices:
                selected_pools.append(pool)
        
        if not selected_pools:
            print("No valid user pools selected.")
        else:
            print(f"\nSelected {len(selected_pools)} user pools for deletion:")
            for pool in selected_pools:
                print(f"  {pool['index']}. {pool['name']} ({pool['id']}) - Users: {pool['user_count']}")
        
        return selected_pools

    def delete_user_pools(self, user_pools):
        """Delete selected user pools without confirmation"""
        print("\nDeleting user pools...")
        
        for pool in user_pools:
            print(f"\nDeleting User Pool: {pool['name']} ({pool['id']})...")
            
            # First check if the user pool has a domain configured
            try:
                domain_response = self.cognito_client.describe_user_pool(
                    UserPoolId=pool['id']
                )
                
                # Check if the user pool has a domain
                if 'Domain' in domain_response['UserPool']:
                    domain = domain_response['UserPool']['Domain']
                    print(f"User pool has a domain configured: {domain}. Deleting domain first...")
                    
                    try:
                        self.cognito_client.delete_user_pool_domain(
                            Domain=domain,
                            UserPoolId=pool['id']
                        )
                        print(f"Domain {domain} deleted successfully.")
                        
                        # Wait a moment for the domain deletion to propagate
                        time.sleep(5)
                    except ClientError as domain_error:
                        print(f"ERROR: Failed to delete domain {domain}: {domain_error}")
                        continue  # Skip this user pool if domain deletion fails
            except ClientError as e:
                print(f"ERROR: Failed to check domain for User Pool {pool['name']} ({pool['id']}): {e}")
                continue  # Skip this user pool if we can't check for domains
            
            # Now delete the user pool
            try:
                # Delete the user pool without confirmation
                self.cognito_client.delete_user_pool(
                    UserPoolId=pool['id']
                )
                print(f"User Pool {pool['name']} ({pool['id']}) deletion initiated.")
                
                # Wait for deletion to complete
                self._wait_for_deletion(pool['id'])
            except ClientError as e:
                print(f"ERROR: Failed to delete User Pool {pool['name']} ({pool['id']}): {e}")
    
    def _wait_for_deletion(self, user_pool_id):
        """Wait for a user pool to be deleted"""
        print(f"Waiting for user pool deletion to complete...")
        max_attempts = 30
        attempts = 0
        
        while attempts < max_attempts:
            try:
                self.cognito_client.describe_user_pool(UserPoolId=user_pool_id)
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
        
        # Fetch all user pools
        user_pools = self.fetch_user_pools()
        
        # Display all user pools
        self.display_user_pools(user_pools)
        
        # Let user select user pools to delete
        selected_pools = self.select_user_pools(user_pools)
        
        # Delete selected user pools without confirmation
        if selected_pools:
            self.delete_user_pools(selected_pools)
        
        print("\nOperation completed.")

if __name__ == "__main__":
    cleaner = CognitoUserPoolCleaner()
    cleaner.run()
