#!/usr/bin/env python3
# Amazon Q Business Resource Cleaner
# This script lists and deletes various Amazon Q Business resources with an interactive menu

import boto3
import sys
import time
from botocore.exceptions import ClientError
from datetime import datetime

class QBusinessCleaner:
    def __init__(self):
        # Use the default region from AWS CLI configuration
        session = boto3.session.Session()
        self.region = session.region_name or "us-east-1"
        self.q_client = boto3.client('qbusiness', region_name=self.region)
        
    def print_header(self):
        """Print a header for the application"""
        print("\n" + "=" * 60)
        print("Amazon Q Business Resource Cleaner".center(60))
        print("=" * 60)
        print(f"Region: {self.region}")
        print("=" * 60 + "\n")

    def fetch_all_resources(self):
        """Fetch all Amazon Q Business resources and return them in a single list"""
        all_resources = []
        resource_index = 1  # Start numbering from 1
        
        # Fetch applications
        print("Fetching Q Business applications...")
        applications = []
        try:
            paginator = self.q_client.get_paginator('list_applications')
            for page in paginator.paginate():
                for app in page.get('applications', []):
                    applications.append(app)
                    all_resources.append({
                        'index': resource_index,
                        'name': app['name'],
                        'id': app['applicationId'],
                        'type': 'Application',
                        'delete_function': self.delete_application
                    })
                    resource_index += 1
        except ClientError as e:
            print(f"Error listing applications: {e}")
        
        # For each application, fetch its resources
        for app in applications:
            app_id = app['applicationId']
            
            # Fetch data sources for this application
            print(f"Fetching data sources for application {app_id}...")
            try:
                ds_paginator = self.q_client.get_paginator('list_data_sources')
                for page in ds_paginator.paginate(applicationId=app_id):
                    for ds in page.get('dataSources', []):
                        all_resources.append({
                            'index': resource_index,
                            'name': ds['name'],
                            'id': ds['dataSourceId'],
                            'application_id': app_id,
                            'type': 'Data Source',
                            'delete_function': self.delete_data_source
                        })
                        resource_index += 1
            except ClientError as e:
                print(f"Error listing data sources for application {app_id}: {e}")
            
            # Fetch indexes for this application
            print(f"Fetching indexes for application {app_id}...")
            try:
                idx_paginator = self.q_client.get_paginator('list_indices')
                for page in idx_paginator.paginate(applicationId=app_id):
                    for idx in page.get('indices', []):
                        all_resources.append({
                            'index': resource_index,
                            'name': idx['name'],
                            'id': idx['indexId'],
                            'application_id': app_id,
                            'type': 'Index',
                            'delete_function': self.delete_index
                        })
                        resource_index += 1
            except ClientError as e:
                print(f"Error listing indexes for application {app_id}: {e}")
            
            # Fetch web experiences for this application
            print(f"Fetching web experiences for application {app_id}...")
            try:
                exp_paginator = self.q_client.get_paginator('list_web_experiences')
                for page in exp_paginator.paginate(applicationId=app_id):
                    for exp in page.get('webExperiences', []):
                        all_resources.append({
                            'index': resource_index,
                            'name': exp['name'],
                            'id': exp['webExperienceId'],
                            'application_id': app_id,
                            'type': 'Web Experience',
                            'delete_function': self.delete_web_experience
                        })
                        resource_index += 1
            except ClientError as e:
                print(f"Error listing web experiences for application {app_id}: {e}")
            
            # Fetch plugins for this application
            print(f"Fetching plugins for application {app_id}...")
            try:
                plugin_paginator = self.q_client.get_paginator('list_plugins')
                for page in plugin_paginator.paginate(applicationId=app_id):
                    for plugin in page.get('plugins', []):
                        all_resources.append({
                            'index': resource_index,
                            'name': plugin['name'],
                            'id': plugin['pluginId'],
                            'application_id': app_id,
                            'type': 'Plugin',
                            'delete_function': self.delete_plugin
                        })
                        resource_index += 1
            except ClientError as e:
                print(f"Error listing plugins for application {app_id}: {e}")
            
            # Fetch retrievers for this application
            print(f"Fetching retrievers for application {app_id}...")
            try:
                retriever_paginator = self.q_client.get_paginator('list_retrievers')
                for page in retriever_paginator.paginate(applicationId=app_id):
                    for retriever in page.get('retrievers', []):
                        all_resources.append({
                            'index': resource_index,
                            'name': retriever['name'],
                            'id': retriever['retrieverId'],
                            'application_id': app_id,
                            'type': 'Retriever',
                            'delete_function': self.delete_retriever
                        })
                        resource_index += 1
            except ClientError as e:
                print(f"Error listing retrievers for application {app_id}: {e}")
        
        return all_resources

    def display_resources(self, resources):
        """Display all resources in a single consolidated view"""
        if not resources:
            print("No Amazon Q Business resources found.")
            return
        
        print("\nAvailable Amazon Q Business Resources:")
        print("-" * 100)
        print(f"{'#':<5} {'Type':<20} {'Name':<30} {'ID':<30} {'Application ID':<15}")
        print("-" * 100)
        
        for resource in resources:
            app_id = resource.get('application_id', 'N/A')
            print(f"{resource['index']:<5} {resource['type']:<20} {resource['name']:<30} {resource['id']:<30} {app_id:<15}")
    
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
                print(f"  {resource['index']}. {resource['type']} - {resource['name']}")
        
        return selected_resources

    def confirm_deletion(self, count):
        """Ask for confirmation before deleting resources"""
        confirm = input(f"\nAre you sure you want to delete these {count} resources? (yes/no): ")
        return confirm.lower() in ['yes', 'y']

    def delete_resources(self, resources):
        """Delete selected resources one by one"""
        print("\nDeleting resources...")
        
        # Sort resources to ensure proper deletion order (applications last)
        sorted_resources = sorted(resources, key=lambda x: 1 if x['type'] == 'Application' else 0)
        
        for resource in sorted_resources:
            print(f"\nDeleting {resource['type']}: {resource['name']} ({resource['id']})...")
            try:
                if resource['type'] == 'Data Source':
                    resource['delete_function'](resource['id'], resource['application_id'])
                elif resource['type'] == 'Index':
                    resource['delete_function'](resource['id'], resource['application_id'])
                elif resource['type'] == 'Web Experience':
                    resource['delete_function'](resource['id'], resource['application_id'])
                elif resource['type'] == 'Plugin':
                    resource['delete_function'](resource['id'], resource['application_id'])
                elif resource['type'] == 'Retriever':
                    resource['delete_function'](resource['id'], resource['application_id'])
                else:
                    resource['delete_function'](resource['id'])
            except Exception as e:
                print(f"ERROR: Failed to delete {resource['type']} {resource['name']}: {e}")
    
    # Resource deletion functions
    def delete_application(self, application_id):
        """Delete a Q Business application"""
        try:
            self.q_client.delete_application(applicationId=application_id)
            print(f"Application {application_id} deletion initiated. This may take several minutes to complete.")
            self._wait_for_deletion('application', application_id)
        except ClientError as e:
            raise Exception(f"Error: {str(e)}")

    def delete_data_source(self, data_source_id, application_id):
        """Delete a Q Business data source"""
        try:
            self.q_client.delete_data_source(
                applicationId=application_id,
                dataSourceId=data_source_id
            )
            print(f"Data source {data_source_id} deletion initiated.")
            self._wait_for_deletion('data_source', data_source_id, application_id)
        except ClientError as e:
            raise Exception(f"Error: {str(e)}")

    def delete_index(self, index_id, application_id):
        """Delete a Q Business index"""
        try:
            self.q_client.delete_index(
                applicationId=application_id,
                indexId=index_id
            )
            print(f"Index {index_id} deletion initiated.")
            self._wait_for_deletion('index', index_id, application_id)
        except ClientError as e:
            raise Exception(f"Error: {str(e)}")

    def delete_web_experience(self, web_experience_id, application_id):
        """Delete a Q Business web experience"""
        try:
            self.q_client.delete_web_experience(
                applicationId=application_id,
                webExperienceId=web_experience_id
            )
            print(f"Web experience {web_experience_id} deletion initiated.")
            self._wait_for_deletion('web_experience', web_experience_id, application_id)
        except ClientError as e:
            raise Exception(f"Error: {str(e)}")

    def delete_plugin(self, plugin_id, application_id):
        """Delete a Q Business plugin"""
        try:
            self.q_client.delete_plugin(
                applicationId=application_id,
                pluginId=plugin_id
            )
            print(f"Plugin {plugin_id} deletion initiated.")
            self._wait_for_deletion('plugin', plugin_id, application_id)
        except ClientError as e:
            raise Exception(f"Error: {str(e)}")

    def delete_retriever(self, retriever_id, application_id):
        """Delete a Q Business retriever"""
        try:
            self.q_client.delete_retriever(
                applicationId=application_id,
                retrieverId=retriever_id
            )
            print(f"Retriever {retriever_id} deletion initiated.")
            self._wait_for_deletion('retriever', retriever_id, application_id)
        except ClientError as e:
            raise Exception(f"Error: {str(e)}")

    def _wait_for_deletion(self, resource_type, resource_id, application_id=None):
        """Wait for a resource to be deleted"""
        print(f"Waiting for {resource_type} deletion to complete...")
        max_attempts = 30
        attempts = 0
        
        while attempts < max_attempts:
            try:
                if resource_type == 'application':
                    self.q_client.get_application(applicationId=resource_id)
                elif resource_type == 'data_source':
                    self.q_client.get_data_source(applicationId=application_id, dataSourceId=resource_id)
                elif resource_type == 'index':
                    self.q_client.get_index(applicationId=application_id, indexId=resource_id)
                elif resource_type == 'web_experience':
                    self.q_client.get_web_experience(applicationId=application_id, webExperienceId=resource_id)
                elif resource_type == 'plugin':
                    self.q_client.get_plugin(applicationId=application_id, pluginId=resource_id)
                elif resource_type == 'retriever':
                    self.q_client.get_retriever(applicationId=application_id, retrieverId=resource_id)
                
                print("Still deleting...")
                time.sleep(10)  # Check every 10 seconds
                attempts += 1
            except ClientError as e:
                if 'ResourceNotFoundException' in str(e) or 'NotFound' in str(e):
                    print(f"{resource_type.capitalize()} {resource_id} successfully deleted.")
                    return
                else:
                    print(f"Error checking {resource_type} status: {str(e)}")
                    return
        
        print(f"Deletion of {resource_type} {resource_id} is taking longer than expected. It may still be in progress.")

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
    cleaner = QBusinessCleaner()
    cleaner.run()
