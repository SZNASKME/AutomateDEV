"""
AWS Utilities - Example Usage
This module demonstrates how to use the AWS action classes with proper credential management.
"""

import os
import sys
import logging
from aws_credentials import AWSCredentialsManager
from aws_config import AWSConfig
from aws_lambda_actions import LambdaActions
from aws_ec2_actions import EC2Actions  
from aws_s3_actions import S3Actions
from aws_ecs_actions import ECSActions
from aws_eks_actions import EKSActions

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_aws_access() -> bool:
    """ตั้งค่าการเชื่อมต่อ AWS อัตโนมัติ"""
    print("🔧 AWS Access Setup")
    print("="*50)
    
    credentials_manager = AWSCredentialsManager()
    
    # Method 1: Auto configuration
    print("🔍 1. Trying auto-detection...")
    if credentials_manager.setup_credentials('auto'):
        print("✅ Auto configuration successful!")
        return True
    
    # Method 2: Environment variables
    print("🌍 2. Checking environment variables...")
    if credentials_manager.setup_credentials('env'):
        print("✅ Environment variables found!")
        return True
    
    # Method 3: AWS Profile
    print("👤 3. Checking AWS profiles...")
    profiles = credentials_manager.list_available_profiles()
    if profiles:
        print(f"📋 Available profiles: {', '.join(profiles)}")
        for profile in profiles:
            if credentials_manager.setup_credentials('profile', profile_name=profile):
                print(f"✅ Using profile: {profile}")
                return True
    
    # Method 4: IAM Role
    print("🔐 4. Checking IAM role...")
    if credentials_manager.setup_credentials('iam_role'):
        print("✅ IAM role credentials found!")
        return True
    
    # Failed to setup
    print("❌ Failed to setup AWS access automatically")
    print("\n" + "="*60)
    print("💡 Please configure AWS credentials using one of these methods:")
    print("="*60)
    print("1️⃣ AWS CLI:")
    print("   pip install awscli")
    print("   aws configure")
    print()
    print("2️⃣ Environment Variables:")
    if os.name == 'nt':  # Windows
        print("   set AWS_ACCESS_KEY_ID=your_access_key")
        print("   set AWS_SECRET_ACCESS_KEY=your_secret_key")
        print("   set AWS_DEFAULT_REGION=us-east-1")
    else:  # Linux/Mac
        print("   export AWS_ACCESS_KEY_ID=your_access_key")
        print("   export AWS_SECRET_ACCESS_KEY=your_secret_key")
        print("   export AWS_DEFAULT_REGION=us-east-1")
    print()
    print("3️⃣ Interactive Setup:")
    print("   python -c \"from aws_credentials import AWSCredentialsManager; AWSCredentialsManager().setup_interactive()\"")
    print("="*60)
    
    return False

def interactive_setup() -> bool:
    """Interactive setup สำหรับ credentials"""
    print("🛠️ Interactive AWS Credentials Setup")
    print("="*50)
    
    credentials_manager = AWSCredentialsManager()
    return credentials_manager.setup_interactive()

def show_current_config():
    """แสดง configuration ปัจจุบัน"""
    print("📊 Current AWS Configuration")
    print("="*50)
    
    # Show config
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

def lambda_example():
    """Example usage of Lambda actions with credential handling"""
    print("\n🚀 AWS Lambda Examples")
    print("="*30)
    
    try:
        # Get configuration
        config = AWSConfig.get_service_config('lambda')
        
        # Initialize Lambda client
        lambda_client = LambdaActions(
            region_name=config['region_name'],
            profile_name=config['profile_name']
        )
        
        # Test connection
        if not lambda_client.test_connection():
            print("❌ Lambda connection failed")
            return
        
        # List functions
        functions = lambda_client.list_functions()
        print(f"📋 Found {len(functions)} Lambda functions")
        
        # Show function names
        if functions:
            print("📝 Function names:")
            for i, func in enumerate(functions[:5], 1):  # Show first 5
                print(f"   {i}. {func['FunctionName']}")
            if len(functions) > 5:
                print(f"   ... and {len(functions) - 5} more")
        
        # Show current identity
        identity = lambda_client.get_current_identity()
        if identity:
            print(f"👤 Connected as: {identity.get('Arn', 'Unknown')}")
    
    except Exception as e:
        print(f"❌ Lambda example error: {e}")
        logger.error(f"Lambda example failed: {e}")

def ec2_example():
    """Example usage of EC2 actions with credential handling"""
    print("\n💻 AWS EC2 Examples")
    print("="*25)
    
    try:
        # Initialize EC2 client
        ec2_client = EC2Actions()
        
        # Test connection
        if not ec2_client.test_connection():
            print("❌ EC2 connection failed")
            return
        
        # List instances
        instances = ec2_client.describe_instances()
        print(f"📋 Found {len(instances)} EC2 instances")
        
        # Show instance details
        running_instances = [i for i in instances if i.get('State', {}).get('Name') == 'running']
        if running_instances:
            print(f"🟢 Running instances: {len(running_instances)}")
            for i, instance in enumerate(running_instances[:3], 1):
                name = 'Unknown'
                for tag in instance.get('Tags', []):
                    if tag['Key'] == 'Name':
                        name = tag['Value']
                        break
                print(f"   {i}. {instance['InstanceId']} ({name}) - {instance['InstanceType']}")
        
    except Exception as e:
        print(f"❌ EC2 example error: {e}")
        logger.error(f"EC2 example failed: {e}")

def s3_example():
    """Example usage of S3 actions with credential handling"""
    print("\n🗄️ AWS S3 Examples")
    print("="*24)
    
    try:
        # Initialize S3 client
        s3_client = S3Actions()
        
        # Test connection
        if not s3_client.test_connection():
            print("❌ S3 connection failed")
            return
        
        # List buckets
        buckets = s3_client.list_buckets()
        print(f"📋 Found {len(buckets)} S3 buckets")
        
        # Show bucket details
        if buckets:
            print("📝 Bucket names:")
            for i, bucket in enumerate(buckets[:5], 1):  # Show first 5
                print(f"   {i}. {bucket['Name']} (Created: {bucket['CreationDate'].strftime('%Y-%m-%d')})")
            if len(buckets) > 5:
                print(f"   ... and {len(buckets) - 5} more")
        
    except Exception as e:
        print(f"❌ S3 example error: {e}")
        logger.error(f"S3 example failed: {e}")

def ecs_example():
    """Example usage of ECS actions with credential handling"""
    print("\n🐳 AWS ECS Examples")
    print("="*25)
    
    try:
        # Initialize ECS client
        ecs_client = ECSActions()
        
        # Test connection
        if not ecs_client.test_connection():
            print("❌ ECS connection failed")
            return
        
        # List clusters
        clusters = ecs_client.list_clusters()
        print(f"📋 Found {len(clusters)} ECS clusters")
        
        # Show cluster details
        if clusters:
            print("📝 Cluster details:")
            for i, cluster in enumerate(clusters[:3], 1):  # Show first 3
                status = cluster.get('status', 'Unknown')
                running_tasks = cluster.get('runningTasksCount', 0)
                print(f"   {i}. {cluster['clusterName']} - {status} ({running_tasks} running tasks)")
        
    except Exception as e:
        print(f"❌ ECS example error: {e}")
        logger.error(f"ECS example failed: {e}")

def eks_example():
    """Example usage of EKS actions with credential handling"""
    print("\n⚙️ AWS EKS Examples")
    print("="*25)
    
    try:
        # Initialize EKS client
        eks_client = EKSActions()
        
        # Test connection
        if not eks_client.test_connection():
            print("❌ EKS connection failed")
            return
        
        # List clusters
        clusters = eks_client.list_clusters()
        print(f"📋 Found {len(clusters)} EKS clusters")
        
        # Show cluster details
        if clusters:
            print("📝 Cluster details:")
            for i, cluster_name in enumerate(clusters[:3], 1):  # Show first 3
                try:
                    details = eks_client.describe_cluster(cluster_name)
                    status = details['cluster']['status']
                    version = details['cluster']['version']
                    print(f"   {i}. {cluster_name} - {status} (v{version})")
                except Exception:
                    print(f"   {i}. {cluster_name} - (Unable to get details)")
        
    except Exception as e:
        print(f"❌ EKS example error: {e}")
        logger.error(f"EKS example failed: {e}")

def comprehensive_example():
    """Comprehensive example using multiple AWS services"""
    print("\n🌟 Comprehensive AWS Example")
    print("="*35)
    
    try:
        print("🔍 Testing all AWS service connections...")
        
        services_status = {}
        
        # Test Lambda
        try:
            lambda_client = LambdaActions()
            services_status['Lambda'] = lambda_client.test_connection()
        except Exception as e:
            services_status['Lambda'] = False
            logger.error(f"Lambda test failed: {e}")
        
        # Test EC2
        try:
            ec2_client = EC2Actions()
            services_status['EC2'] = ec2_client.test_connection()
        except Exception as e:
            services_status['EC2'] = False
            logger.error(f"EC2 test failed: {e}")
        
        # Test S3
        try:
            s3_client = S3Actions()
            services_status['S3'] = s3_client.test_connection()
        except Exception as e:
            services_status['S3'] = False
            logger.error(f"S3 test failed: {e}")
        
        # Test ECS
        try:
            ecs_client = ECSActions()
            services_status['ECS'] = ecs_client.test_connection()
        except Exception as e:
            services_status['ECS'] = False
            logger.error(f"ECS test failed: {e}")
        
        # Test EKS
        try:
            eks_client = EKSActions()
            services_status['EKS'] = eks_client.test_connection()
        except Exception as e:
            services_status['EKS'] = False
            logger.error(f"EKS test failed: {e}")
        
        # Show results
        print("\n📊 Service Connection Status:")
        for service, status in services_status.items():
            emoji = "✅" if status else "❌"
            print(f"   {emoji} {service}: {'Connected' if status else 'Failed'}")
        
        successful_services = sum(services_status.values())
        total_services = len(services_status)
        
        print(f"\n🎯 Summary: {successful_services}/{total_services} services connected successfully")
        
        if successful_services == total_services:
            print("🎉 All AWS services are accessible!")
        elif successful_services > 0:
            print("⚠️ Some AWS services may have permission issues")
        else:
            print("❌ No AWS services are accessible - check your credentials")
        
    except Exception as e:
        print(f"❌ Comprehensive example error: {e}")
        logger.error(f"Comprehensive example failed: {e}")

def main_menu():
    """Main interactive menu"""
    while True:
        print("\n" + "="*60)
        print("🚀 AWS Actions Examples - Interactive Menu")
        print("="*60)
        print("1. 🔧 Setup AWS Credentials (Interactive)")
        print("2. 📊 Show Current Configuration")
        print("3. 🚀 Lambda Examples")
        print("4. 💻 EC2 Examples")
        print("5. 🗄️  S3 Examples")
        print("6. 🐳 ECS Examples")
        print("7. ⚙️  EKS Examples")
        print("8. 🌟 Test All Services")
        print("9. 🔄 Run All Examples")
        print("0. 🚪 Exit")
        print("="*60)
        
        try:
            choice = input("Enter your choice (0-9): ").strip()
            
            if choice == '0':
                print("👋 Goodbye!")
                break
            elif choice == '1':
                interactive_setup()
            elif choice == '2':
                show_current_config()
            elif choice == '3':
                lambda_example()
            elif choice == '4':
                ec2_example()
            elif choice == '5':
                s3_example()
            elif choice == '6':
                ecs_example()
            elif choice == '7':
                eks_example()
            elif choice == '8':
                comprehensive_example()
            elif choice == '9':
                run_all_examples()
            else:
                print("❌ Invalid choice. Please select 0-9.")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def run_all_examples():
    """Run all examples sequentially"""
    print("\n🔄 Running All AWS Examples")
    print("="*40)
    
    # Check credentials first
    if not setup_aws_access():
        return
    
    # Show configuration
    show_current_config()
    
    # Run examples
    lambda_example()
    ec2_example() 
    s3_example()
    ecs_example()
    eks_example()
    
    # Run comprehensive test
    comprehensive_example()

if __name__ == "__main__":
    """Run interactive menu or all examples"""
    print("🚀 AWS Actions Examples with Credential Management")
    print("="*60)
    print("Version 1.1.0 - Enhanced with credential management")
    print("="*60)
    
    # Check if running in interactive mode
    if len(sys.argv) > 1:
        if sys.argv[1] == '--interactive' or sys.argv[1] == '-i':
            main_menu()
        elif sys.argv[1] == '--setup':
            interactive_setup()
        elif sys.argv[1] == '--config':
            show_current_config()
        elif sys.argv[1] == '--test':
            comprehensive_example()
        elif sys.argv[1] == '--help' or sys.argv[1] == '-h':
            print("\nUsage options:")
            print("  python examples.py --interactive    # Interactive menu")
            print("  python examples.py --setup          # Setup credentials")
            print("  python examples.py --config         # Show configuration")
            print("  python examples.py --test           # Test all services")
            print("  python examples.py --help           # Show this help")
            print("  python examples.py                  # Run all examples")
        else:
            print(f"❌ Unknown option: {sys.argv[1]}")
            print("Use --help for available options")
    else:
        # Default: Run all examples
        run_all_examples()
        
        # Ask if user wants interactive mode
        print("\n" + "="*50)
        try:
            choice = input("Would you like to use interactive mode? (y/n): ").lower().strip()
            if choice in ['y', 'yes']:
                main_menu()
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
    
    print("\n🎉 AWS Actions Examples completed!")
    print("📖 For more information, check README.md")
    print("🔧 Need help? Run with --help option")