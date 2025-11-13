#!/usr/bin/env python3
"""
AWS Utils CLI - Command Line Interface
ใช้งาน AWS Actions ผ่าน command line
"""

import sys
import argparse
from aws_credentials import AWSCredentialsManager
from aws_config import AWSConfig

def setup_credentials(args):
    """Setup AWS credentials"""
    print("🔧 AWS Credentials Setup")
    print("="*30)
    
    credentials_manager = AWSCredentialsManager()
    
    if args.interactive:
        success = credentials_manager.setup_interactive()
    else:
        success = credentials_manager.setup_credentials('auto')
    
    if success:
        print("✅ AWS credentials setup successful!")
        
        # Show identity
        identity = credentials_manager.get_current_identity()
        if identity:
            print(f"\n👤 Connected as:")
            print(f"   Account: {identity.get('Account', 'Unknown')}")
            print(f"   User/Role: {identity.get('Arn', 'Unknown')}")
    else:
        print("❌ AWS credentials setup failed!")
        return 1
    
    return 0

def show_config(args):
    """Show current AWS configuration"""
    AWSConfig.print_current_config()
    
    # Show identity
    try:
        credentials_manager = AWSCredentialsManager()
        identity = credentials_manager.get_current_identity()
        
        if identity:
            print("\n🔐 Current AWS Identity:")
            print(f"Account ID: {identity.get('Account', 'Unknown')}")
            print(f"User/Role:  {identity.get('Arn', 'Unknown')}")
            print(f"User ID:    {identity.get('UserId', 'Unknown')}")
    except Exception as e:
        print(f"❌ Failed to get identity: {e}")
    
    return 0

def test_connection(args):
    """Test AWS connection"""
    print("🔍 Testing AWS Connection")
    print("="*30)
    
    credentials_manager = AWSCredentialsManager()
    
    if credentials_manager.test_connection():
        print("✅ AWS connection successful!")
        
        # Test specific services if requested
        if hasattr(args, 'services') and args.services:
            from aws_lambda_actions import LambdaActions
            from aws_ec2_actions import EC2Actions
            from aws_s3_actions import S3Actions
            from aws_ecs_actions import ECSActions
            from aws_eks_actions import EKSActions
            
            service_classes = {
                'lambda': LambdaActions,
                'ec2': EC2Actions,
                's3': S3Actions,
                'ecs': ECSActions,
                'eks': EKSActions
            }
            
            print(f"\n🧪 Testing specific services: {', '.join(args.services)}")
            
            for service in args.services:
                if service in service_classes:
                    try:
                        client = service_classes[service]()
                        if client.test_connection():
                            print(f"✅ {service.upper()} service: Connected")
                        else:
                            print(f"❌ {service.upper()} service: Failed")
                    except Exception as e:
                        print(f"❌ {service.upper()} service: Error - {e}")
                else:
                    print(f"❌ Unknown service: {service}")
        
        return 0
    else:
        print("❌ AWS connection failed!")
        return 1

def list_resources(args):
    """List AWS resources"""
    print(f"📋 Listing {args.resource_type} resources")
    print("="*40)
    
    try:
        if args.resource_type == 'lambda':
            from aws_lambda_actions import LambdaActions
            client = LambdaActions()
            functions = client.list_functions()
            
            if functions:
                print(f"Found {len(functions)} Lambda functions:")
                for i, func in enumerate(functions, 1):
                    print(f"  {i:2d}. {func['FunctionName']}")
                    print(f"      Runtime: {func['Runtime']}")
                    print(f"      Updated: {func['LastModified']}")
            else:
                print("No Lambda functions found")
                
        elif args.resource_type == 'ec2':
            from aws_ec2_actions import EC2Actions
            client = EC2Actions()
            instances = client.describe_instances()
            
            if instances:
                print(f"Found {len(instances)} EC2 instances:")
                for i, instance in enumerate(instances, 1):
                    name = 'No Name'
                    for tag in instance.get('Tags', []):
                        if tag['Key'] == 'Name':
                            name = tag['Value']
                            break
                    
                    state = instance['State']['Name']
                    print(f"  {i:2d}. {instance['InstanceId']} ({name})")
                    print(f"      Type: {instance['InstanceType']}")
                    print(f"      State: {state}")
            else:
                print("No EC2 instances found")
                
        elif args.resource_type == 's3':
            from aws_s3_actions import S3Actions
            client = S3Actions()
            buckets = client.list_buckets()
            
            if buckets:
                print(f"Found {len(buckets)} S3 buckets:")
                for i, bucket in enumerate(buckets, 1):
                    print(f"  {i:2d}. {bucket['Name']}")
                    print(f"      Created: {bucket['CreationDate'].strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print("No S3 buckets found")
                
        elif args.resource_type == 'ecs':
            from aws_ecs_actions import ECSActions
            client = ECSActions()
            clusters = client.list_clusters()
            
            if clusters:
                print(f"Found {len(clusters)} ECS clusters:")
                for i, cluster in enumerate(clusters, 1):
                    print(f"  {i:2d}. {cluster['clusterName']}")
                    print(f"      Status: {cluster['status']}")
                    print(f"      Tasks: {cluster.get('runningTasksCount', 0)} running")
            else:
                print("No ECS clusters found")
                
        elif args.resource_type == 'eks':
            from aws_eks_actions import EKSActions
            client = EKSActions()
            clusters = client.list_clusters()
            
            if clusters:
                print(f"Found {len(clusters)} EKS clusters:")
                for i, cluster_name in enumerate(clusters, 1):
                    try:
                        details = client.describe_cluster(cluster_name)
                        status = details['cluster']['status']
                        version = details['cluster']['version']
                        print(f"  {i:2d}. {cluster_name}")
                        print(f"      Status: {status}")
                        print(f"      Version: {version}")
                    except Exception:
                        print(f"  {i:2d}. {cluster_name} (details unavailable)")
            else:
                print("No EKS clusters found")
                
        else:
            print(f"❌ Unknown resource type: {args.resource_type}")
            return 1
            
    except Exception as e:
        print(f"❌ Error listing {args.resource_type} resources: {e}")
        return 1
    
    return 0

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="AWS Utils CLI - Manage AWS services from command line",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s setup --interactive          # Interactive credential setup
  %(prog)s config                       # Show current configuration  
  %(prog)s test --services lambda s3    # Test specific services
  %(prog)s list lambda                  # List Lambda functions
  %(prog)s list ec2                     # List EC2 instances
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Setup AWS credentials')
    setup_parser.add_argument('--interactive', '-i', action='store_true',
                             help='Use interactive setup')
    setup_parser.set_defaults(func=setup_credentials)
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Show current configuration')
    config_parser.set_defaults(func=show_config)
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test AWS connection')
    test_parser.add_argument('--services', nargs='+', 
                            choices=['lambda', 'ec2', 's3', 'ecs', 'eks'],
                            help='Test specific services')
    test_parser.set_defaults(func=test_connection)
    
    # List command
    list_parser = subparsers.add_parser('list', help='List AWS resources')
    list_parser.add_argument('resource_type', 
                            choices=['lambda', 'ec2', 's3', 'ecs', 'eks'],
                            help='Type of resources to list')
    list_parser.set_defaults(func=list_resources)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Show help if no command provided
    if not args.command:
        parser.print_help()
        return 0
    
    # Execute command
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n👋 Operation cancelled")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())