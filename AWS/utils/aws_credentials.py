import boto3
import os
from typing import Optional, Dict, Any
from botocore.exceptions import NoCredentialsError, ClientError, ProfileNotFound
import logging

logger = logging.getLogger(__name__)

class AWSCredentialsManager:
    """
    AWS Credentials Management
    จัดการการเชื่อมต่อและ authentication กับ AWS
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    def setup_credentials(self, method: str = 'auto', **kwargs) -> bool:
        """
        ตั้งค่า AWS credentials
        
        Args:
            method: วิธีการตั้งค่า ('auto', 'profile', 'env', 'iam_role', 'manual')
            **kwargs: อาร์กิวเมนต์เพิ่มเติมสำหรับแต่ละ method
        
        Returns:
            bool: สำเร็จหรือไม่
        """
        try:
            if method == 'auto':
                return self._auto_configure()
            elif method == 'profile':
                profile_name = kwargs.get('profile_name', 'default')
                return self._configure_with_profile(profile_name)
            elif method == 'env':
                return self._configure_with_env()
            elif method == 'iam_role':
                return self._configure_with_iam_role()
            elif method == 'manual':
                return self._configure_manually(**kwargs)
            else:
                raise ValueError(f"Unknown method: {method}")
                
        except Exception as e:
            self.logger.error(f"Failed to setup credentials: {e}")
            return False
    
    def _auto_configure(self) -> bool:
        """ตั้งค่าอัตโนมัติ ตามลำดับความสำคัญ"""
        try:
            # ลองใช้ default session
            session = boto3.Session()
            credentials = session.get_credentials()
            
            if credentials:
                # ทดสอบความถูกต้อง
                if self._validate_credentials(credentials):
                    self.logger.info("✅ AWS credentials found automatically")
                    return True
                else:
                    self.logger.warning("❌ Invalid AWS credentials")
                    return False
            else:
                self.logger.warning("❌ No AWS credentials found")
                return False
                
        except Exception as e:
            self.logger.error(f"Auto configuration failed: {e}")
            return False
    
    def _configure_with_profile(self, profile_name: str = 'default') -> bool:
        """ใช้ AWS Profile"""
        try:
            session = boto3.Session(profile_name=profile_name)
            credentials = session.get_credentials()
            
            if credentials and self._validate_credentials(credentials):
                self.logger.info(f"✅ Using AWS profile: {profile_name}")
                return True
            else:
                self.logger.error(f"❌ Profile {profile_name} not found or invalid")
                return False
                
        except ProfileNotFound:
            self.logger.error(f"❌ AWS profile '{profile_name}' not found")
            return False
        except Exception as e:
            self.logger.error(f"Profile configuration failed: {e}")
            return False
    
    def _configure_with_env(self) -> bool:
        """ใช้ Environment Variables"""
        required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.logger.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
            self._show_env_setup_help()
            return False
        
        try:
            # ทดสอบ credentials
            session = boto3.Session()
            if self.test_connection(session=session):
                self.logger.info("✅ Using environment variables for AWS credentials")
                return True
            else:
                return False
        except Exception as e:
            self.logger.error(f"Environment variables configuration failed: {e}")
            return False
    
    def _configure_with_iam_role(self) -> bool:
        """ใช้ IAM Role (สำหรับ EC2/Lambda/ECS)"""
        try:
            session = boto3.Session()
            credentials = session.get_credentials()
            
            if credentials and hasattr(credentials, 'token') and credentials.token:
                if self.test_connection(session=session):
                    self.logger.info("✅ Using IAM role credentials")
                    return True
            
            self.logger.error("❌ IAM role credentials not available")
            return False
                
        except Exception as e:
            self.logger.error(f"IAM role configuration failed: {e}")
            return False
    
    def _configure_manually(self, access_key: str, secret_key: str, session_token: str = None) -> bool:
        """กำหนด credentials แบบ manual"""
        try:
            session = boto3.Session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                aws_session_token=session_token
            )
            
            if self.test_connection(session=session):
                self.logger.info("✅ Manual credentials configured successfully")
                return True
            else:
                self.logger.error("❌ Invalid manual credentials")
                return False
                
        except Exception as e:
            self.logger.error(f"Manual configuration failed: {e}")
            return False
    
    def _validate_credentials(self, credentials) -> bool:
        """ตรวจสอบความถูกต้องของ credentials"""
        try:
            if not credentials:
                return False
            
            # ตรวจสอบว่ามี access key และ secret key
            access_key = credentials.access_key
            secret_key = credentials.secret_key
            
            return bool(access_key and secret_key)
        except Exception:
            return False
    
    def test_connection(self, region_name: str = 'us-east-1', session: boto3.Session = None) -> bool:
        """ทดสอบการเชื่อมต่อ AWS"""
        try:
            if session:
                sts_client = session.client('sts', region_name=region_name)
            else:
                sts_client = boto3.client('sts', region_name=region_name)
            
            response = sts_client.get_caller_identity()
            
            self.logger.info("🔗 Successfully connected to AWS")
            self.logger.info(f"📝 Account ID: {response.get('Account')}")
            self.logger.info(f"👤 User/Role: {response.get('Arn')}")
            return True
            
        except NoCredentialsError:
            self.logger.error("❌ No AWS credentials found")
            self._show_credentials_setup_help()
            return False
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'InvalidUserID.NotFound':
                self.logger.error("❌ Invalid AWS credentials")
            elif error_code == 'AccessDenied':
                self.logger.error("❌ Access denied - check your permissions")
            else:
                self.logger.error(f"❌ AWS API error: {error_code}")
            return False
        except Exception as e:
            self.logger.error(f"❌ AWS connection test failed: {e}")
            return False
    
    def get_current_identity(self, region_name: str = 'us-east-1') -> Optional[Dict[str, Any]]:
        """ดูข้อมูล identity ปัจจุบัน"""
        try:
            sts_client = boto3.client('sts', region_name=region_name)
            return sts_client.get_caller_identity()
        except Exception as e:
            self.logger.error(f"Failed to get identity: {e}")
            return None
    
    def list_available_profiles(self) -> list:
        """แสดงรายการ AWS profiles ที่มีอยู่"""
        try:
            session = boto3.Session()
            return session.available_profiles
        except Exception as e:
            self.logger.error(f"Failed to list profiles: {e}")
            return []
    
    def get_current_region(self) -> str:
        """ดู region ปัจจุบัน"""
        try:
            session = boto3.Session()
            return session.region_name or 'us-east-1'
        except Exception:
            return 'us-east-1'
    
    def _show_credentials_setup_help(self):
        """แสดงคำแนะนำการตั้งค่า credentials"""
        print("\n" + "="*60)
        print("🔧 AWS Credentials Setup Help")
        print("="*60)
        print("Please configure AWS credentials using one of these methods:\n")
        
        print("1️⃣ AWS CLI (Recommended):")
        print("   pip install awscli")
        print("   aws configure\n")
        
        print("2️⃣ Environment Variables:")
        print("   Windows:")
        print("   set AWS_ACCESS_KEY_ID=your_access_key")
        print("   set AWS_SECRET_ACCESS_KEY=your_secret_key")
        print("   set AWS_DEFAULT_REGION=us-east-1\n")
        print("   Linux/Mac:")
        print("   export AWS_ACCESS_KEY_ID=your_access_key")
        print("   export AWS_SECRET_ACCESS_KEY=your_secret_key")
        print("   export AWS_DEFAULT_REGION=us-east-1\n")
        
        print("3️⃣ AWS Profile:")
        print("   aws configure --profile myprofile\n")
        
        print("4️⃣ IAM Roles (for EC2/Lambda/ECS):")
        print("   Attach IAM role to your compute resource\n")
        
        print("🔗 More info: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html")
        print("="*60)
    
    def _show_env_setup_help(self):
        """แสดงคำแนะนำการตั้งค่า environment variables"""
        print("\n" + "="*50)
        print("🌍 Environment Variables Setup")
        print("="*50)
        print("Required environment variables:")
        print("  - AWS_ACCESS_KEY_ID")
        print("  - AWS_SECRET_ACCESS_KEY")
        print("  - AWS_DEFAULT_REGION (optional)")
        print("  - AWS_SESSION_TOKEN (optional, for temporary credentials)")
        print("="*50)
    
    @staticmethod
    def create_session(profile_name: str = None, region_name: str = 'us-east-1', 
                      access_key: str = None, secret_key: str = None, 
                      session_token: str = None) -> boto3.Session:
        """สร้าง boto3 session"""
        session_kwargs = {'region_name': region_name}
        
        if profile_name:
            session_kwargs['profile_name'] = profile_name
        elif access_key and secret_key:
            session_kwargs.update({
                'aws_access_key_id': access_key,
                'aws_secret_access_key': secret_key
            })
            if session_token:
                session_kwargs['aws_session_token'] = session_token
        
        return boto3.Session(**session_kwargs)
    
    def setup_interactive(self) -> bool:
        """Interactive setup สำหรับ credentials"""
        print("\n🔧 AWS Credentials Interactive Setup")
        print("="*40)
        
        methods = {
            '1': ('auto', 'Auto-detect credentials'),
            '2': ('profile', 'Use AWS profile'),
            '3': ('env', 'Use environment variables'),
            '4': ('iam_role', 'Use IAM role'),
            '5': ('manual', 'Enter credentials manually')
        }
        
        print("Choose credential method:")
        for key, (method, description) in methods.items():
            print(f"  {key}. {description}")
        
        try:
            choice = input("\nEnter choice (1-5): ").strip()
            
            if choice not in methods:
                print("❌ Invalid choice")
                return False
            
            method = methods[choice][0]
            
            if method == 'auto':
                return self.setup_credentials('auto')
            
            elif method == 'profile':
                profiles = self.list_available_profiles()
                if profiles:
                    print(f"Available profiles: {', '.join(profiles)}")
                profile_name = input("Enter profile name (default): ").strip() or 'default'
                return self.setup_credentials('profile', profile_name=profile_name)
            
            elif method == 'env':
                print("Make sure these environment variables are set:")
                print("  - AWS_ACCESS_KEY_ID")
                print("  - AWS_SECRET_ACCESS_KEY")
                input("Press Enter when ready...")
                return self.setup_credentials('env')
            
            elif method == 'iam_role':
                print("Using IAM role credentials (for EC2/Lambda/ECS)")
                return self.setup_credentials('iam_role')
            
            elif method == 'manual':
                access_key = input("Enter AWS Access Key ID: ").strip()
                secret_key = input("Enter AWS Secret Access Key: ").strip()
                session_token = input("Enter Session Token (optional): ").strip() or None
                
                return self.setup_credentials('manual', 
                                            access_key=access_key,
                                            secret_key=secret_key,
                                            session_token=session_token)
            
        except KeyboardInterrupt:
            print("\n❌ Setup cancelled")
            return False
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False