import boto3
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from .aws_credentials import AWSCredentialsManager
from .aws_config import AWSConfig

logger = logging.getLogger(__name__)

class SecretsManagerActions:
    """
    AWS Secrets Manager Actions
    จัดการ passwords และ secrets ใน AWS Secrets Manager
    """
    
    def __init__(self, region_name: str = None, profile_name: str = None, auto_setup: bool = True):
        # Get configuration
        config = AWSConfig.get_config()
        self.region_name = region_name or config['region_name']
        self.profile_name = profile_name or config['profile_name']
        
        # Setup logging
        logging.basicConfig(level=getattr(logging, config['log_level'], logging.INFO))
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Setup credentials
        self.credentials_manager = AWSCredentialsManager()
        
        if auto_setup:
            self._setup_session()
    
    def _setup_session(self):
        """ตั้งค่า boto3 session และ clients"""
        try:
            # สร้าง session
            self.session = AWSCredentialsManager.create_session(
                profile_name=self.profile_name,
                region_name=self.region_name
            )
            
            # สร้าง clients
            self.secrets_client = self.session.client('secretsmanager')
            self.ssm_client = self.session.client('ssm')
            self.iam_client = self.session.client('iam')
            
            # ทดสอบการเชื่อมต่อ
            if not self.credentials_manager.test_connection(region_name=self.region_name):
                raise Exception("Failed to connect to AWS")
                
            self.logger.info(f"✅ Secrets Manager client initialized successfully in region: {self.region_name}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup Secrets Manager client: {e}")
            self.logger.info("💡 Please configure AWS credentials first")
            raise
    
    def test_connection(self) -> bool:
        """ทดสอบการเชื่อมต่อ Secrets Manager service"""
        try:
            # ลองเรียก list_secrets เพื่อทดสอบ
            self.secrets_client.list_secrets(MaxResults=1)
            self.logger.info("✅ Secrets Manager service connection successful")
            return True
        except Exception as e:
            self.logger.error(f"❌ Secrets Manager service connection failed: {e}")
            return False
    
    # === SECRETS MANAGER ===
    
    def create_secret(self, secret_name: str, secret_value: str, 
                     description: str = "", tags: Dict[str, str] = None) -> Dict[str, Any]:
        """สร้าง secret ใหม่ใน Secrets Manager"""
        try:
            params = {
                'Name': secret_name,
                'SecretString': secret_value,
                'Description': description
            }
            
            if tags:
                params['Tags'] = [{'Key': k, 'Value': v} for k, v in tags.items()]
            
            response = self.secrets_client.create_secret(**params)
            self.logger.info(f"✅ Created secret: {secret_name}")
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Error creating secret {secret_name}: {e}")
            raise
    
    def get_secret(self, secret_name: str) -> str:
        """ดึงค่า secret จาก Secrets Manager"""
        try:
            response = self.secrets_client.get_secret_value(SecretId=secret_name)
            self.logger.info(f"✅ Retrieved secret: {secret_name}")
            return response['SecretString']
            
        except Exception as e:
            self.logger.error(f"❌ Error getting secret {secret_name}: {e}")
            raise
    
    def update_secret(self, secret_name: str, secret_value: str) -> Dict[str, Any]:
        """อัพเดต secret"""
        try:
            response = self.secrets_client.update_secret(
                SecretId=secret_name,
                SecretString=secret_value
            )
            self.logger.info(f"✅ Updated secret: {secret_name}")
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Error updating secret {secret_name}: {e}")
            raise
    
    def delete_secret(self, secret_name: str, force_delete: bool = False, 
                     recovery_window_days: int = 30) -> Dict[str, Any]:
        """ลบ secret"""
        try:
            if force_delete:
                response = self.secrets_client.delete_secret(
                    SecretId=secret_name,
                    ForceDeleteWithoutRecovery=True
                )
            else:
                response = self.secrets_client.delete_secret(
                    SecretId=secret_name,
                    RecoveryWindowInDays=recovery_window_days
                )
            
            self.logger.info(f"✅ Deleted secret: {secret_name}")
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Error deleting secret {secret_name}: {e}")
            raise
    
    def list_secrets(self, max_results: int = 100) -> List[Dict[str, Any]]:
        """แสดงรายการ secrets ทั้งหมด"""
        try:
            response = self.secrets_client.list_secrets(MaxResults=max_results)
            secrets = response['SecretList']
            self.logger.info(f"✅ Found {len(secrets)} secrets")
            return secrets
            
        except Exception as e:
            self.logger.error(f"❌ Error listing secrets: {e}")
            raise
    
    # === PARAMETER STORE ===
    
    def put_parameter(self, name: str, value: str, secure: bool = True,
                     description: str = "", parameter_type: str = None,
                     tags: Dict[str, str] = None) -> Dict[str, Any]:
        """เก็บ parameter ใน Parameter Store"""
        try:
            if parameter_type is None:
                parameter_type = 'SecureString' if secure else 'String'
            
            params = {
                'Name': name,
                'Value': value,
                'Type': parameter_type,
                'Description': description,
                'Overwrite': True
            }
            
            if tags:
                params['Tags'] = [{'Key': k, 'Value': v} for k, v in tags.items()]
            
            response = self.ssm_client.put_parameter(**params)
            self.logger.info(f"✅ Put parameter: {name}")
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Error putting parameter {name}: {e}")
            raise
    
    def get_parameter(self, name: str, decrypt: bool = True) -> str:
        """ดึงค่า parameter จาก Parameter Store"""
        try:
            response = self.ssm_client.get_parameter(
                Name=name,
                WithDecryption=decrypt
            )
            self.logger.info(f"✅ Retrieved parameter: {name}")
            return response['Parameter']['Value']
            
        except Exception as e:
            self.logger.error(f"❌ Error getting parameter {name}: {e}")
            raise
    
    def get_parameters(self, names: List[str], decrypt: bool = True) -> Dict[str, str]:
        """ดึงหลาย parameters พร้อมกัน"""
        try:
            response = self.ssm_client.get_parameters(
                Names=names,
                WithDecryption=decrypt
            )
            
            result = {}
            for param in response['Parameters']:
                result[param['Name']] = param['Value']
            
            self.logger.info(f"✅ Retrieved {len(result)} parameters")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error getting parameters: {e}")
            raise
    
    def delete_parameter(self, name: str) -> Dict[str, Any]:
        """ลบ parameter"""
        try:
            response = self.ssm_client.delete_parameter(Name=name)
            self.logger.info(f"✅ Deleted parameter: {name}")
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Error deleting parameter {name}: {e}")
            raise
    
    # === IAM PASSWORD MANAGEMENT ===
    
    def create_user_with_password(self, username: str, password: str, 
                                 require_reset: bool = True, 
                                 tags: Dict[str, str] = None) -> Dict[str, Any]:
        """สร้าง IAM user พร้อมรหัสผ่าน"""
        try:
            # สร้าง user
            user_params = {'UserName': username}
            if tags:
                user_params['Tags'] = [{'Key': k, 'Value': v} for k, v in tags.items()]
            
            self.iam_client.create_user(**user_params)
            
            # สร้าง login profile
            response = self.iam_client.create_login_profile(
                UserName=username,
                Password=password,
                PasswordResetRequired=require_reset
            )
            
            self.logger.info(f"✅ Created user with password: {username}")
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Error creating user {username}: {e}")
            raise
    
    def update_login_profile(self, username: str, password: str, 
                           require_reset: bool = False) -> Dict[str, Any]:
        """อัพเดตรหัสผ่าน IAM user"""
        try:
            response = self.iam_client.update_login_profile(
                UserName=username,
                Password=password,
                PasswordResetRequired=require_reset
            )
            
            self.logger.info(f"✅ Updated password for user: {username}")
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Error updating password for user {username}: {e}")
            raise
    
    # === UTILITY METHODS ===
    
    def create_database_secret(self, secret_name: str, username: str, 
                              password: str, host: str, port: int, 
                              database: str, engine: str = "mysql") -> Dict[str, Any]:
        """สร้าง secret สำหรับ database"""
        secret_value = json.dumps({
            'username': username,
            'password': password,
            'host': host,
            'port': port,
            'database': database,
            'engine': engine
        })
        
        return self.create_secret(
            secret_name=secret_name,
            secret_value=secret_value,
            description=f"Database credentials for {database}",
            tags={'Type': 'Database', 'Database': database, 'Engine': engine}
        )
    
    def get_database_credentials(self, secret_name: str) -> Dict[str, Any]:
        """ดึงข้อมูล database credentials"""
        secret_value = self.get_secret(secret_name)
        return json.loads(secret_value)
    
    def create_api_key_secret(self, secret_name: str, api_key: str, 
                             service_name: str, description: str = "") -> Dict[str, Any]:
        """สร้าง secret สำหรับ API key"""
        secret_value = json.dumps({
            'api_key': api_key,
            'service': service_name,
            'created_at': str(datetime.utcnow())
        })
        
        return self.create_secret(
            secret_name=secret_name,
            secret_value=secret_value,
            description=description or f"API key for {service_name}",
            tags={'Type': 'APIKey', 'Service': service_name}
        )
    
    def rotate_secret(self, secret_name: str, lambda_function_arn: str, 
                     automatically_after_days: int = 30) -> Dict[str, Any]:
        """เปิดการหมุนเวียน secret อัตโนมัติ"""
        try:
            response = self.secrets_client.rotate_secret(
                SecretId=secret_name,
                RotationLambdaARN=lambda_function_arn,
                RotationRules={'AutomaticallyAfterDays': automatically_after_days}
            )
            
            self.logger.info(f"✅ Enabled rotation for secret: {secret_name}")
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Error rotating secret {secret_name}: {e}")
            raise
    
    def generate_random_password(self, length: int = 32, 
                                exclude_characters: str = "",
                                include_space: bool = False,
                                require_each_included_type: bool = True) -> str:
        """สร้างรหัสผ่านแบบสุ่ม"""
        try:
            response = self.secrets_client.get_random_password(
                PasswordLength=length,
                ExcludeCharacters=exclude_characters,
                IncludeSpace=include_space,
                RequireEachIncludedType=require_each_included_type
            )
            
            password = response['RandomPassword']
            self.logger.info(f"✅ Generated random password of length {length}")
            return password
            
        except Exception as e:
            self.logger.error(f"❌ Error generating random password: {e}")
            raise