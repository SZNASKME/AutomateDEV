import boto3
import json
import logging
from typing import Dict, Any, Optional, List
from .aws_credentials import AWSCredentialsManager
from .aws_config import AWSConfig

logger = logging.getLogger(__name__)

class LambdaActions:
    """AWS Lambda actions handler with improved credential management"""
    
    def __init__(self, region_name: str = None, profile_name: str = None, auto_setup: bool = True):
        # Get configuration
        config = AWSConfig.get_service_config('lambda')
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
        """ตั้งค่า boto3 session และ client"""
        try:
            # สร้าง session
            self.session = AWSCredentialsManager.create_session(
                profile_name=self.profile_name,
                region_name=self.region_name
            )
            
            # สร้าง client
            self.lambda_client = self.session.client('lambda')
            
            # ทดสอบการเชื่อมต่อ
            if not self.credentials_manager.test_connection(region_name=self.region_name):
                raise Exception("Failed to connect to AWS")
                
            self.logger.info(f"✅ Lambda client initialized successfully in region: {self.region_name}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup Lambda client: {e}")
            self.logger.info("💡 Please configure AWS credentials first")
            raise
    
    def test_connection(self) -> bool:
        """ทดสอบการเชื่อมต่อ Lambda service"""
        try:
            # ลองเรียก list_functions เพื่อทดสอบ
            self.lambda_client.list_functions(MaxItems=1)
            self.logger.info("✅ Lambda service connection successful")
            return True
        except Exception as e:
            self.logger.error(f"❌ Lambda service connection failed: {e}")
            return False
    
    def get_current_identity(self) -> Optional[Dict[str, Any]]:
        """ดูข้อมูล identity ปัจจุบัน"""
        return self.credentials_manager.get_current_identity(region_name=self.region_name)
    
    def create_function(self, 
                       function_name: str,
                       runtime: str,
                       role: str,
                       handler: str,
                       zip_file: bytes,
                       description: str = "",
                       timeout: int = 3,
                       memory_size: int = 128,
                       environment_variables: Optional[Dict[str, str]] = None,
                       tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create a new Lambda function"""
        try:
            function_config = {
                'FunctionName': function_name,
                'Runtime': runtime,
                'Role': role,
                'Handler': handler,
                'Code': {'ZipFile': zip_file},
                'Description': description,
                'Timeout': timeout,
                'MemorySize': memory_size
            }
            
            if environment_variables:
                function_config['Environment'] = {'Variables': environment_variables}
            
            if tags:
                function_config['Tags'] = tags
            
            response = self.lambda_client.create_function(**function_config)
            logger.info(f"Successfully created Lambda function: {function_name}")
            return response
        
        except Exception as e:
            logger.error(f"Error creating Lambda function {function_name}: {str(e)}")
            raise
    
    def update_function_code(self, function_name: str, zip_file: bytes) -> Dict[str, Any]:
        """Update Lambda function code"""
        try:
            response = self.lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=zip_file
            )
            logger.info(f"Successfully updated code for Lambda function: {function_name}")
            return response
        
        except Exception as e:
            logger.error(f"Error updating Lambda function code {function_name}: {str(e)}")
            raise
    
    def update_function_configuration(self, 
                                    function_name: str,
                                    runtime: Optional[str] = None,
                                    handler: Optional[str] = None,
                                    description: Optional[str] = None,
                                    timeout: Optional[int] = None,
                                    memory_size: Optional[int] = None,
                                    environment_variables: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Update Lambda function configuration"""
        try:
            update_config = {'FunctionName': function_name}
            
            if runtime:
                update_config['Runtime'] = runtime
            if handler:
                update_config['Handler'] = handler
            if description:
                update_config['Description'] = description
            if timeout:
                update_config['Timeout'] = timeout
            if memory_size:
                update_config['MemorySize'] = memory_size
            if environment_variables:
                update_config['Environment'] = {'Variables': environment_variables}
            
            response = self.lambda_client.update_function_configuration(**update_config)
            logger.info(f"Successfully updated configuration for Lambda function: {function_name}")
            return response
        
        except Exception as e:
            logger.error(f"Error updating Lambda function configuration {function_name}: {str(e)}")
            raise
    
    def invoke_function(self, 
                       function_name: str,
                       payload: Dict[str, Any],
                       invocation_type: str = 'RequestResponse') -> Dict[str, Any]:
        """Invoke Lambda function"""
        try:
            response = self.lambda_client.invoke(
                FunctionName=function_name,
                InvocationType=invocation_type,
                Payload=json.dumps(payload)
            )
            
            if response.get('Payload'):
                response['Payload'] = response['Payload'].read().decode('utf-8')
            
            logger.info(f"Successfully invoked Lambda function: {function_name}")
            return response
        
        except Exception as e:
            logger.error(f"Error invoking Lambda function {function_name}: {str(e)}")
            raise
    
    def delete_function(self, function_name: str) -> Dict[str, Any]:
        """Delete Lambda function"""
        try:
            response = self.lambda_client.delete_function(FunctionName=function_name)
            logger.info(f"Successfully deleted Lambda function: {function_name}")
            return response
        
        except Exception as e:
            logger.error(f"Error deleting Lambda function {function_name}: {str(e)}")
            raise
    
    def list_functions(self) -> List[Dict[str, Any]]:
        """List all Lambda functions"""
        try:
            response = self.lambda_client.list_functions()
            functions = response.get('Functions', [])
            logger.info(f"Found {len(functions)} Lambda functions")
            return functions
        
        except Exception as e:
            logger.error(f"Error listing Lambda functions: {str(e)}")
            raise
    
    def get_function(self, function_name: str) -> Dict[str, Any]:
        """Get Lambda function details"""
        try:
            response = self.lambda_client.get_function(FunctionName=function_name)
            logger.info(f"Successfully retrieved Lambda function details: {function_name}")
            return response
        
        except Exception as e:
            logger.error(f"Error getting Lambda function {function_name}: {str(e)}")
            raise
    
    def add_permission(self, 
                      function_name: str,
                      statement_id: str,
                      action: str,
                      principal: str,
                      source_arn: Optional[str] = None) -> Dict[str, Any]:
        """Add permission to Lambda function"""
        try:
            permission_config = {
                'FunctionName': function_name,
                'StatementId': statement_id,
                'Action': action,
                'Principal': principal
            }
            
            if source_arn:
                permission_config['SourceArn'] = source_arn
            
            response = self.lambda_client.add_permission(**permission_config)
            logger.info(f"Successfully added permission to Lambda function: {function_name}")
            return response
        
        except Exception as e:
            logger.error(f"Error adding permission to Lambda function {function_name}: {str(e)}")
            raise