"""
AWS Actions Package
This package provides action classes for various AWS services including:
- Lambda (Serverless Functions)
- EC2 (Elastic Compute Cloud)
- S3 (Simple Storage Service) 
- ECS (Elastic Container Service)
- EKS (Elastic Kubernetes Service)
- Secrets Manager (Password & Secret Management)

Features:
- Comprehensive credential management
- Automatic AWS authentication
- Error handling and logging
- Configuration management
- Interactive setup tools
- Password and secrets management
"""

from .aws_credentials import AWSCredentialsManager
from .aws_config import AWSConfig
from .aws_lambda_actions import LambdaActions
from .aws_ec2_actions import EC2Actions
from .aws_s3_actions import S3Actions
from .aws_ecs_actions import ECSActions
from .aws_eks_actions import EKSActions
from .aws_secrets_actions import SecretsManagerActions

__all__ = [
    'AWSCredentialsManager',
    'AWSConfig',
    'LambdaActions',
    'EC2Actions', 
    'S3Actions',
    'ECSActions',
    'EKSActions',
    'SecretsManagerActions'
]

__version__ = '1.1.0'

# Convenience function for quick setup
def setup_aws_credentials(interactive: bool = False) -> bool:
    """
    Quick setup function for AWS credentials
    
    Args:
        interactive: Use interactive setup if True
        
    Returns:
        bool: True if setup successful
    """
    credentials_manager = AWSCredentialsManager()
    
    if interactive:
        return credentials_manager.setup_interactive()
    else:
        return credentials_manager.setup_credentials('auto')