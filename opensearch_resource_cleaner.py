#!/usr/bin/env python3
# OpenSearch Resource Cleaner
# This script lists and deletes various OpenSearch resources with an interactive menu

import boto3
import sys
import time
from botocore.exceptions import ClientError
from datetime import datetime

class OpenSearchCleaner:
    def __init__(self):
        # Use the default region from AWS CLI configuration
        session = boto3.session.Session()
        self.region = session.region_name or "us-east-1"
        self.client = boto3.client('opensearch', region_name=self.region)
        self.serverless_client = boto3.client('opensearchserverless', region_name=self.region)
        
    def print_header(self):
        """Print a header for the application"""
        print("\n" + "=" * 60)
        print("OpenSearch Resource Cleaner".center(60))
        print("=" * 60)
        print(f"Region: {self.region}")
        print("=" * 60 + "\n")

    def fetch_all_resources(self):
        """Fetch all OpenSearch resources and return them in a single list"""
        all_resources = []
        resource_index = 1  # Start numbering from 1
        
        # Fetch domains
        print("Fetching OpenSearch domains...")
        try:
            response = self.client.list_domain_names()
            for domain in response.get('DomainNames', []):
                all_resources.append({
                    'index': resource_index,
                    'name': domain['DomainName'],
                    'id': domain['DomainName'],
                    'type': 'Domain',
                    'delete_function': self.delete_domain
                })
                resource_index += 1
        except ClientError as e:
            print(f"Error listing domains: {e}")
        
        # Fetch serverless collections
        print("Fetching OpenSearch serverless collections...")
        try:
            response = self.serverless_client.list_collections()
            for collection in response.get('collectionSummaries', []):
                all_resources.append({
                    'index': resource_index,
                    'name': collection['name'],
                    'id': collection['id'],
                    'type': 'Serverless Collection',
                    'delete_function': self.delete_serverless_collection
                })
                resource_index += 1
        except ClientError as e:
            print(f"Error listing serverless collections: {e}")
        
        # Fetch VPC endpoints
        print("Fetching OpenSearch VPC endpoints...")
        try:
            response = self.serverless_client.list_vpc_endpoints()
            for endpoint in response.get('vpcEndpointSummaries', []):
                all_resources.append({
                    'index': resource_index,
                    'name': endpoint['id'],
                    'id': endpoint['id'],
                    'type': 'VPC Endpoint',
                    'delete_function': self.delete_vpc_endpoint
                })
                resource_index += 1
        except ClientError as e:
            print(f"Error listing VPC endpoints: {e}")
        
        # Fetch data access policies
        print("Fetching OpenSearch data access policies...")
        try:
            response = self.serverless_client.list_access_policies(type='data')
            for policy in response.get('accessPolicySummaries', []):
                all_resources.append({
                    'index': resource_index,
                    'name': policy['name'],
                    'id': policy['name'],
                    'type': 'Data Access Policy',
                    'delete_function': self.delete_data_access_policy
                })
                resource_index += 1
        except ClientError as e:
            print(f"Error listing data access policies: {e}")
        
        # Fetch network policies
        print("Fetching OpenSearch network policies...")
        try:
            response = self.serverless_client.list_security_policies(type='network')
            for policy in response.get('securityPolicySummaries', []):
                all_resources.append({
                    'index': resource_index,
                    'name': policy['name'],
                    'id': policy['name'],
                    'type': 'Network Policy',
                    'delete_function': self.delete_network_policy
                })
                resource_index += 1
        except ClientError as e:
            print(f"Error listing network policies: {e}")
        
        # Fetch encryption policies
        print("Fetching OpenSearch encryption policies...")
        try:
            response = self.serverless_client.list_security_policies(type='encryption')
            for policy in response.get('securityPolicySummaries', []):
                all_resources.append({
                    'index': resource_index,
                    'name': policy['name'],
                    'id': policy['name'],
                    'type': 'Encryption Policy',
                    'delete_function': self.delete_encryption_policy
                })
                resource_index += 1
        except ClientError as e:
            print(f"Error listing encryption policies: {e}")
        
        return all_resources

    def display_resources(self, resources):
        """Display all resources in a single consolidated view"""
        if not resources:
            print("No OpenSearch resources found.")
            return
        
        print("\nAvailable OpenSearch Resources:")
        print("-" * 80)
        print(f"{'#':<5} {'Type':<25} {'Name':<30} {'ID':<20}")
        print("-" * 80)
        
        for resource in resources:
            print(f"{resource['index']:<5} {resource['type']:<25} {resource['name']:<30} {resource['id']:<20}")
    
    def select_resources(self, resources):
        """Let user select resources by number"""
        if not resources:
            return []
        
        selection = input("\nEnter the number(s) of resources to delete (comma-separated): ")
        
        selected_indices = []
        try:
            for num in selection.split(','):
                selected_indices.append(int(num.strip()))
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
                print(f"  {resource['index']}. {resource['type']} - {resource['name']}")
        
        return selected_resources

    def confirm_deletion(self, count):
        """Ask for confirmation before deleting resources"""
        confirm = input(f"\nAre you sure you want to delete these {count} resources? (yes/no): ")
        return confirm.lower() in ['yes', 'y']

    def delete_resources(self, resources):
        """Delete selected resources one by one"""
        print("\nDeleting resources...")
        
        for resource in resources:
            print(f"\nDeleting {resource['type']}: {resource['name']} ({resource['id']})...")
            try:
                resource['delete_function'](resource['id'])
            except Exception as e:
                print(f"ERROR: Failed to delete {resource['type']} {resource['name']}: {e}")
    
    # Resource deletion functions
    def delete_domain(self, domain_name):
        """Delete an OpenSearch domain"""
        try:
            self.client.delete_domain(DomainName=domain_name)
            print(f"Domain {domain_name} deletion initiated. This may take several minutes to complete.")
        except ClientError as e:
            raise Exception(f"Error: {str(e)}")

    def delete_serverless_collection(self, collection_id):
        """Delete an OpenSearch serverless collection"""
        try:
            self.serverless_client.delete_collection(id=collection_id)
            print(f"Serverless collection {collection_id} deletion initiated.")
            
            # Wait for deletion to complete
            print("Waiting for deletion to complete...")
            while True:
                try:
                    response = self.serverless_client.batch_get_collection(ids=[collection_id])
                    status = response.get('collectionDetails', [{}])[0].get('status')
                    if status == 'DELETING':
                        print("Still deleting...")
                        time.sleep(10)  # Check every 10 seconds
                    else:
                        print(f"Unexpected status: {status}")
                        break
                except ClientError as e:
                    if 'ResourceNotFoundException' in str(e):
                        print(f"Collection {collection_id} successfully deleted.")
                        break
                    else:
                        raise Exception(f"Error checking collection status: {str(e)}")
        except ClientError as e:
            raise Exception(f"Error: {str(e)}")

    def delete_vpc_endpoint(self, endpoint_id):
        """Delete an OpenSearch VPC endpoint"""
        try:
            self.serverless_client.delete_vpc_endpoint(id=endpoint_id)
            print(f"VPC endpoint {endpoint_id} deletion initiated.")
        except ClientError as e:
            raise Exception(f"Error: {str(e)}")

    def delete_data_access_policy(self, policy_name):
        """Delete an OpenSearch data access policy"""
        try:
            self.serverless_client.delete_access_policy(name=policy_name, type='data')
            print(f"Data access policy {policy_name} deleted.")
        except ClientError as e:
            raise Exception(f"Error: {str(e)}")

    def delete_network_policy(self, policy_name):
        """Delete an OpenSearch network policy"""
        try:
            self.serverless_client.delete_security_policy(name=policy_name, type='network')
            print(f"Network policy {policy_name} deleted.")
        except ClientError as e:
            raise Exception(f"Error: {str(e)}")

    def delete_encryption_policy(self, policy_name):
        """Delete an OpenSearch encryption policy"""
        try:
            self.serverless_client.delete_security_policy(name=policy_name, type='encryption')
            print(f"Encryption policy {policy_name} deleted.")
        except ClientError as e:
            raise Exception(f"Error: {str(e)}")

    def run(self):
        """Main execution flow"""
        self.print_header()
        
        # Fetch all resources at once
        all_resources = self.fetch_all_resources()
        
        # Display all resources in a consolidated view
        self.display_resources(all_resources)
        
        # Let user select resources to delete
        selected_resources = self.select_resources(all_resources)
        
        # Confirm and delete if resources were selected
        if selected_resources and self.confirm_deletion(len(selected_resources)):
            self.delete_resources(selected_resources)
        
        print("\nOperation completed.")

if __name__ == "__main__":
    cleaner = OpenSearchCleaner()
    cleaner.run()
