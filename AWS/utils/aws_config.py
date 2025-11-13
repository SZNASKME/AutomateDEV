import os
from typing import Dict, Any, Optional

class AWSConfig:
    """AWS Configuration Settings"""
    
    # Default settings
    DEFAULT_REGION = 'us-east-1'
    DEFAULT_PROFILE = None
    
    # Timeout settings (seconds)
    DEFAULT_TIMEOUT = 30
    LAMBDA_TIMEOUT = 60
    ECS_TIMEOUT = 300
    EKS_TIMEOUT = 600
    
    # Retry settings
    MAX_RETRIES = 3
    
    # Logging settings
    LOG_LEVEL = 'INFO'
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """ดึง configuration จาก environment variables หรือใช้ default"""
        return {
            'region_name': os.getenv('AWS_DEFAULT_REGION', cls.DEFAULT_REGION),
            'profile_name': os.getenv('AWS_PROFILE', cls.DEFAULT_PROFILE),
            'timeout': int(os.getenv('AWS_TIMEOUT', cls.DEFAULT_TIMEOUT)),
            'max_retries': int(os.getenv('AWS_MAX_RETRIES', cls.MAX_RETRIES)),
            'log_level': os.getenv('AWS_LOG_LEVEL', cls.LOG_LEVEL)
        }
    
    @classmethod
    def get_credentials_from_env(cls) -> Dict[str, str]:
        """ดึง credentials จาก environment variables"""
        return {
            'aws_access_key_id': os.getenv('AWS_ACCESS_KEY_ID', ''),
            'aws_secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY', ''),
            'aws_session_token': os.getenv('AWS_SESSION_TOKEN', ''),
        }
    
    @classmethod
    def get_service_config(cls, service_name: str) -> Dict[str, Any]:
        """ดึง configuration เฉพาะ service"""
        base_config = cls.get_config()
        
        service_configs = {
            'lambda': {
                **base_config,
                'timeout': int(os.getenv('AWS_LAMBDA_TIMEOUT', cls.LAMBDA_TIMEOUT))
            },
            'ecs': {
                **base_config,
                'timeout': int(os.getenv('AWS_ECS_TIMEOUT', cls.ECS_TIMEOUT))
            },
            'eks': {
                **base_config,
                'timeout': int(os.getenv('AWS_EKS_TIMEOUT', cls.EKS_TIMEOUT))
            }
        }
        
        return service_configs.get(service_name, base_config)
    
    @classmethod
    def validate_region(cls, region: str) -> bool:
        """ตรวจสอบว่า region ถูกต้องหรือไม่"""
        valid_regions = [
            'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
            'ap-northeast-1', 'ap-northeast-2', 'ap-southeast-1', 'ap-southeast-2',
            'ap-south-1', 'eu-west-1', 'eu-west-2', 'eu-central-1',
            'sa-east-1', 'ca-central-1'
        ]
        return region in valid_regions
    
    @classmethod
    def get_available_regions(cls) -> list:
        """รายการ regions ที่รองรับ"""
        return [
            'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
            'ap-northeast-1', 'ap-northeast-2', 'ap-southeast-1', 'ap-southeast-2',
            'ap-south-1', 'eu-west-1', 'eu-west-2', 'eu-central-1',
            'sa-east-1', 'ca-central-1'
        ]
    
    @classmethod
    def setup_environment(cls, 
                         access_key: str, 
                         secret_key: str, 
                         region: str = None, 
                         session_token: str = None):
        """ตั้งค่า environment variables"""
        os.environ['AWS_ACCESS_KEY_ID'] = access_key
        os.environ['AWS_SECRET_ACCESS_KEY'] = secret_key
        
        if region:
            os.environ['AWS_DEFAULT_REGION'] = region
        else:
            os.environ['AWS_DEFAULT_REGION'] = cls.DEFAULT_REGION
            
        if session_token:
            os.environ['AWS_SESSION_TOKEN'] = session_token
    
    @classmethod
    def clear_environment(cls):
        """ล้าง AWS environment variables"""
        env_vars = [
            'AWS_ACCESS_KEY_ID',
            'AWS_SECRET_ACCESS_KEY', 
            'AWS_SESSION_TOKEN',
            'AWS_DEFAULT_REGION',
            'AWS_PROFILE'
        ]
        
        for var in env_vars:
            if var in os.environ:
                del os.environ[var]
    
    @classmethod
    def print_current_config(cls):
        """แสดง configuration ปัจจุบัน"""
        config = cls.get_config()
        print("\n" + "="*40)
        print("🔧 Current AWS Configuration")
        print("="*40)
        
        for key, value in config.items():
            if value:
                print(f"{key:15}: {value}")
            else:
                print(f"{key:15}: Not set")
        
        print("\n📍 Environment Variables:")
        env_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_DEFAULT_REGION', 'AWS_PROFILE']
        for var in env_vars:
            value = os.getenv(var)
            if value:
                if 'KEY' in var:
                    print(f"{var:25}: {'*' * 20}")  # Hide sensitive data
                else:
                    print(f"{var:25}: {value}")
            else:
                print(f"{var:25}: Not set")
        print("="*40)