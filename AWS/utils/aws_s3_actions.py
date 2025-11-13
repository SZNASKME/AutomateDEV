import boto3
import json
import logging
from typing import Dict, Any, Optional, List, Union
from botocore.exceptions import ClientError
from .aws_credentials import AWSCredentialsManager
from .aws_config import AWSConfig

logger = logging.getLogger(__name__)

class S3Actions:
    """AWS S3 actions handler with improved credential management"""
    
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
            self.s3_client = self.session.client('s3')
            self.s3_resource = self.session.resource('s3')
            
            # ทดสอบการเชื่อมต่อ
            if not self.credentials_manager.test_connection(region_name=self.region_name):
                raise Exception("Failed to connect to AWS")
                
            self.logger.info(f"✅ S3 client initialized successfully in region: {self.region_name}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup S3 client: {e}")
            self.logger.info("💡 Please configure AWS credentials first")
            raise
    
    def test_connection(self) -> bool:
        """ทดสอบการเชื่อมต่อ S3 service"""
        try:
            # ลองเรียก list_buckets เพื่อทดสอบ
            self.s3_client.list_buckets()
            self.logger.info("✅ S3 service connection successful")
            return True
        except Exception as e:
            self.logger.error(f"❌ S3 service connection failed: {e}")
            return False
    
    def create_bucket(self, 
                     bucket_name: str,
                     region: Optional[str] = None,
                     acl: str = 'private',
                     tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create S3 bucket"""
        try:
            create_config = {'Bucket': bucket_name, 'ACL': acl}
            
            # LocationConstraint is not needed for us-east-1
            if region and region != 'us-east-1':
                create_config['CreateBucketConfiguration'] = {'LocationConstraint': region}
            
            response = self.s3_client.create_bucket(**create_config)
            
            # Add tags if provided
            if tags:
                self.put_bucket_tagging(bucket_name, tags)
            
            logger.info(f"Successfully created S3 bucket: {bucket_name}")
            return response
        
        except Exception as e:
            logger.error(f"Error creating S3 bucket {bucket_name}: {str(e)}")
            raise
    
    def delete_bucket(self, bucket_name: str, force: bool = False) -> Dict[str, Any]:
        """Delete S3 bucket"""
        try:
            # If force is True, delete all objects first
            if force:
                self.delete_all_objects(bucket_name)
            
            response = self.s3_client.delete_bucket(Bucket=bucket_name)
            logger.info(f"Successfully deleted S3 bucket: {bucket_name}")
            return response
        
        except Exception as e:
            logger.error(f"Error deleting S3 bucket {bucket_name}: {str(e)}")
            raise
    
    def upload_file(self, 
                   file_path: str,
                   bucket_name: str,
                   object_key: str,
                   extra_args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Upload file to S3"""
        try:
            self.s3_client.upload_file(
                Filename=file_path,
                Bucket=bucket_name,
                Key=object_key,
                ExtraArgs=extra_args
            )
            logger.info(f"Successfully uploaded file to S3: {object_key}")
            return {"Status": "Success", "Bucket": bucket_name, "Key": object_key}
        
        except Exception as e:
            logger.error(f"Error uploading file to S3 {bucket_name}/{object_key}: {str(e)}")
            raise
    
    def download_file(self, 
                     bucket_name: str,
                     object_key: str,
                     file_path: str) -> Dict[str, Any]:
        """Download file from S3"""
        try:
            self.s3_client.download_file(
                Bucket=bucket_name,
                Key=object_key,
                Filename=file_path
            )
            logger.info(f"Successfully downloaded file from S3: {object_key}")
            return {"Status": "Success", "Bucket": bucket_name, "Key": object_key, "LocalPath": file_path}
        
        except Exception as e:
            logger.error(f"Error downloading file from S3 {bucket_name}/{object_key}: {str(e)}")
            raise
    
    def upload_object(self, 
                     bucket_name: str,
                     object_key: str,
                     data: Union[str, bytes],
                     content_type: Optional[str] = None,
                     metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Upload object to S3"""
        try:
            put_config = {
                'Bucket': bucket_name,
                'Key': object_key,
                'Body': data
            }
            
            if content_type:
                put_config['ContentType'] = content_type
            if metadata:
                put_config['Metadata'] = metadata
            
            response = self.s3_client.put_object(**put_config)
            logger.info(f"Successfully uploaded object to S3: {object_key}")
            return response
        
        except Exception as e:
            logger.error(f"Error uploading object to S3 {bucket_name}/{object_key}: {str(e)}")
            raise
    
    def get_object(self, bucket_name: str, object_key: str) -> Dict[str, Any]:
        """Get object from S3"""
        try:
            response = self.s3_client.get_object(Bucket=bucket_name, Key=object_key)
            logger.info(f"Successfully retrieved object from S3: {object_key}")
            return response
        
        except Exception as e:
            logger.error(f"Error getting object from S3 {bucket_name}/{object_key}: {str(e)}")
            raise
    
    def delete_object(self, bucket_name: str, object_key: str) -> Dict[str, Any]:
        """Delete object from S3"""
        try:
            response = self.s3_client.delete_object(Bucket=bucket_name, Key=object_key)
            logger.info(f"Successfully deleted object from S3: {object_key}")
            return response
        
        except Exception as e:
            logger.error(f"Error deleting object from S3 {bucket_name}/{object_key}: {str(e)}")
            raise
    
    def delete_objects(self, bucket_name: str, object_keys: List[str]) -> Dict[str, Any]:
        """Delete multiple objects from S3"""
        try:
            delete_objects = [{'Key': key} for key in object_keys]
            response = self.s3_client.delete_objects(
                Bucket=bucket_name,
                Delete={'Objects': delete_objects}
            )
            logger.info(f"Successfully deleted {len(object_keys)} objects from S3")
            return response
        
        except Exception as e:
            logger.error(f"Error deleting objects from S3 {bucket_name}: {str(e)}")
            raise
    
    def delete_all_objects(self, bucket_name: str) -> Dict[str, Any]:
        """Delete all objects from S3 bucket"""
        try:
            # List all objects
            objects = self.list_objects(bucket_name)
            
            if not objects:
                logger.info(f"No objects to delete in bucket: {bucket_name}")
                return {"Status": "No objects to delete"}
            
            # Delete in batches of 1000 (S3 limit)
            batch_size = 1000
            deleted_count = 0
            
            for i in range(0, len(objects), batch_size):
                batch = objects[i:i + batch_size]
                object_keys = [obj['Key'] for obj in batch]
                self.delete_objects(bucket_name, object_keys)
                deleted_count += len(object_keys)
            
            logger.info(f"Successfully deleted {deleted_count} objects from S3 bucket: {bucket_name}")
            return {"Status": "Success", "DeletedCount": deleted_count}
        
        except Exception as e:
            logger.error(f"Error deleting all objects from S3 bucket {bucket_name}: {str(e)}")
            raise
    
    def list_objects(self, 
                    bucket_name: str,
                    prefix: Optional[str] = None,
                    max_keys: int = 1000) -> List[Dict[str, Any]]:
        """List objects in S3 bucket"""
        try:
            list_config = {'Bucket': bucket_name, 'MaxKeys': max_keys}
            if prefix:
                list_config['Prefix'] = prefix
            
            response = self.s3_client.list_objects_v2(**list_config)
            objects = response.get('Contents', [])
            
            logger.info(f"Found {len(objects)} objects in S3 bucket: {bucket_name}")
            return objects
        
        except Exception as e:
            logger.error(f"Error listing objects in S3 bucket {bucket_name}: {str(e)}")
            raise
    
    def list_buckets(self) -> List[Dict[str, Any]]:
        """List all S3 buckets"""
        try:
            response = self.s3_client.list_buckets()
            buckets = response.get('Buckets', [])
            logger.info(f"Found {len(buckets)} S3 buckets")
            return buckets
        
        except Exception as e:
            logger.error(f"Error listing S3 buckets: {str(e)}")
            raise
    
    def copy_object(self, 
                   source_bucket: str,
                   source_key: str,
                   dest_bucket: str,
                   dest_key: str,
                   metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Copy object between S3 buckets/keys"""
        try:
            copy_source = {'Bucket': source_bucket, 'Key': source_key}
            copy_config = {
                'CopySource': copy_source,
                'Bucket': dest_bucket,
                'Key': dest_key
            }
            
            if metadata:
                copy_config['Metadata'] = metadata
                copy_config['MetadataDirective'] = 'REPLACE'
            
            response = self.s3_client.copy_object(**copy_config)
            logger.info(f"Successfully copied object from {source_bucket}/{source_key} to {dest_bucket}/{dest_key}")
            return response
        
        except Exception as e:
            logger.error(f"Error copying object: {str(e)}")
            raise
    
    def generate_presigned_url(self, 
                              bucket_name: str,
                              object_key: str,
                              expiration: int = 3600,
                              http_method: str = 'GET') -> str:
        """Generate presigned URL for S3 object"""
        try:
            url = self.s3_client.generate_presigned_url(
                ClientMethod='get_object' if http_method == 'GET' else 'put_object',
                Params={'Bucket': bucket_name, 'Key': object_key},
                ExpiresIn=expiration
            )
            logger.info(f"Generated presigned URL for S3 object: {object_key}")
            return url
        
        except Exception as e:
            logger.error(f"Error generating presigned URL for {bucket_name}/{object_key}: {str(e)}")
            raise
    
    def put_bucket_policy(self, bucket_name: str, policy: Dict[str, Any]) -> Dict[str, Any]:
        """Set bucket policy"""
        try:
            response = self.s3_client.put_bucket_policy(
                Bucket=bucket_name,
                Policy=json.dumps(policy)
            )
            logger.info(f"Successfully set bucket policy for: {bucket_name}")
            return response
        
        except Exception as e:
            logger.error(f"Error setting bucket policy for {bucket_name}: {str(e)}")
            raise
    
    def put_bucket_tagging(self, bucket_name: str, tags: Dict[str, str]) -> Dict[str, Any]:
        """Set bucket tags"""
        try:
            tag_set = [{'Key': key, 'Value': value} for key, value in tags.items()]
            response = self.s3_client.put_bucket_tagging(
                Bucket=bucket_name,
                Tagging={'TagSet': tag_set}
            )
            logger.info(f"Successfully set bucket tags for: {bucket_name}")
            return response
        
        except Exception as e:
            logger.error(f"Error setting bucket tags for {bucket_name}: {str(e)}")
            raise
    
    def enable_versioning(self, bucket_name: str) -> Dict[str, Any]:
        """Enable versioning on S3 bucket"""
        try:
            response = self.s3_client.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={'Status': 'Enabled'}
            )
            logger.info(f"Successfully enabled versioning for bucket: {bucket_name}")
            return response
        
        except Exception as e:
            logger.error(f"Error enabling versioning for bucket {bucket_name}: {str(e)}")
            raise