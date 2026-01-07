#!/usr/bin/env python3
"""
OpenStack Swift Console Manager
A command-line interface for managing OpenStack Swift object storage.

Usage:
    python swift_console_manager.py

Requirements:
    pip install python-swiftclient

Environment Variables:
    OS_AUTH_URL: Authentication URL
    OS_USERNAME: Username
    OS_PASSWORD: Password
    OS_PROJECT_NAME: Project name
    OS_PROJECT_DOMAIN_NAME: Project domain (default: Default)
    OS_USER_DOMAIN_NAME: User domain (default: Default)
"""

import os
import sys
import cmd
import argparse
from swiftclient import Connection
from swiftclient.exceptions import ClientException


class SwiftConsoleManager(cmd.Cmd):
    """Command-line interface for OpenStack Swift operations."""

    intro = 'Welcome to Swift Console Manager. Type help or ? to list commands.\n'
    prompt = '(swift) '

    def __init__(self, conn):
        super().__init__()
        self.conn = conn

    def do_list_containers(self, arg):
        """List all containers."""
        try:
            containers = self.conn.get_account()[1]
            if containers:
                print("Containers:")
                for container in containers:
                    print(f"  {container['name']} ({container['count']} objects, {container['bytes']} bytes)")
            else:
                print("No containers found.")
        except ClientException as e:
            print(f"Error listing containers: {e}")

    def do_create_container(self, arg):
        """Create a new container. Usage: create_container <container_name>"""
        if not arg:
            print("Usage: create_container <container_name>")
            return
        try:
            self.conn.put_container(arg)
            print(f"Container '{arg}' created successfully.")
        except ClientException as e:
            print(f"Error creating container: {e}")

    def do_delete_container(self, arg):
        """Delete a container. Usage: delete_container <container_name>"""
        if not arg:
            print("Usage: delete_container <container_name>")
            return
        try:
            self.conn.delete_container(arg)
            print(f"Container '{arg}' deleted successfully.")
        except ClientException as e:
            print(f"Error deleting container: {e}")

    def do_list_objects(self, arg):
        """List objects in a container. Usage: list_objects <container_name>"""
        if not arg:
            print("Usage: list_objects <container_name>")
            return
        try:
            container_name = arg
            objects = self.conn.get_container(container_name)[1]
            if objects:
                print(f"Objects in '{container_name}':")
                for obj in objects:
                    print(f"  {obj['name']} ({obj['bytes']} bytes, {obj['last_modified']})")
            else:
                print(f"No objects found in '{container_name}'.")
        except ClientException as e:
            print(f"Error listing objects: {e}")

    def do_upload_object(self, arg):
        """Upload a file to a container. Usage: upload_object <container_name> <local_file_path> [object_name]"""
        args = arg.split()
        if len(args) < 2:
            print("Usage: upload_object <container_name> <local_file_path> [object_name]")
            return
        container_name = args[0]
        local_file = args[1]
        object_name = args[2] if len(args) > 2 else os.path.basename(local_file)

        if not os.path.isfile(local_file):
            print(f"Local file '{local_file}' does not exist.")
            return

        try:
            with open(local_file, 'rb') as f:
                self.conn.put_object(container_name, object_name, f)
            print(f"File '{local_file}' uploaded as '{object_name}' to '{container_name}'.")
        except ClientException as e:
            print(f"Error uploading object: {e}")
        except IOError as e:
            print(f"Error reading local file: {e}")

    def do_download_object(self, arg):
        """Download an object from a container. Usage: download_object <container_name> <object_name> [local_file_path]"""
        args = arg.split()
        if len(args) < 2:
            print("Usage: download_object <container_name> <object_name> [local_file_path]")
            return
        container_name = args[0]
        object_name = args[1]
        local_file = args[2] if len(args) > 2 else object_name

        try:
            resp_headers, obj_contents = self.conn.get_object(container_name, object_name)
            with open(local_file, 'wb') as f:
                f.write(obj_contents)
            print(f"Object '{object_name}' downloaded from '{container_name}' to '{local_file}'.")
        except ClientException as e:
            print(f"Error downloading object: {e}")
        except IOError as e:
            print(f"Error writing local file: {e}")

    def do_delete_object(self, arg):
        """Delete an object from a container. Usage: delete_object <container_name> <object_name>"""
        args = arg.split()
        if len(args) != 2:
            print("Usage: delete_object <container_name> <object_name>")
            return
        container_name = args[0]
        object_name = args[1]

        try:
            self.conn.delete_object(container_name, object_name)
            print(f"Object '{object_name}' deleted from '{container_name}'.")
        except ClientException as e:
            print(f"Error deleting object: {e}")

    def do_quit(self, arg):
        """Exit the console."""
        print("Goodbye!")
        return True

    def do_exit(self, arg):
        """Exit the console."""
        return self.do_quit(arg)


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='OpenStack Swift Console Manager')
    parser.add_argument('--auth-url', default=os.getenv('OS_AUTH_URL'),
                        help='Authentication URL')
    parser.add_argument('--username', default=os.getenv('OS_USERNAME'),
                        help='Username')
    parser.add_argument('--password', default=os.getenv('OS_PASSWORD'),
                        help='Password')
    parser.add_argument('--project-name', default=os.getenv('OS_PROJECT_NAME'),
                        help='Project name')
    parser.add_argument('--project-domain', default=os.getenv('OS_PROJECT_DOMAIN_NAME', 'Default'),
                        help='Project domain name')
    parser.add_argument('--user-domain', default=os.getenv('OS_USER_DOMAIN_NAME', 'Default'),
                        help='User domain name')

    args = parser.parse_args()

    # Check required environment variables or arguments
    required = ['auth_url', 'username', 'password', 'project_name']
    missing = [k for k in required if not getattr(args, k)]
    if missing:
        print(f"Missing required parameters: {', '.join(missing)}")
        print("Please set environment variables or provide as arguments.")
        print("Required: OS_AUTH_URL, OS_USERNAME, OS_PASSWORD, OS_PROJECT_NAME")
        sys.exit(1)

    # Create Swift connection
    try:
        conn = Connection(
            authurl=args.auth_url,
            user=args.username,
            key=args.password,
            auth_version='3',
            os_options={
                'project_name': args.project_name,
                'project_domain_name': args.project_domain,
                'user_domain_name': args.user_domain
            }
        )
        # Test connection
        conn.get_account()
    except ClientException as e:
        print(f"Failed to connect to Swift: {e}")
        sys.exit(1)

    # Start the console
    SwiftConsoleManager(conn).cmdloop()


if __name__ == '__main__':
    main()