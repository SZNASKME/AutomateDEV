import boto3
import logging
from typing import Dict, Any, Optional, List
from botocore.exceptions import ClientError
from .aws_credentials import AWSCredentialsManager
from .aws_config import AWSConfig

logger = logging.getLogger(__name__)

class EC2Actions:
    """AWS EC2 actions handler with improved credential management"""
    
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
            self.ec2_client = self.session.client('ec2')
            self.ec2_resource = self.session.resource('ec2')
            
            # ทดสอบการเชื่อมต่อ
            if not self.credentials_manager.test_connection(region_name=self.region_name):
                raise Exception("Failed to connect to AWS")
                
            self.logger.info(f"✅ EC2 client initialized successfully in region: {self.region_name}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup EC2 client: {e}")
            self.logger.info("💡 Please configure AWS credentials first")
            raise
    
    def test_connection(self) -> bool:
        """ทดสอบการเชื่อมต่อ EC2 service"""
        try:
            # ลองเรียก describe_regions เพื่อทดสอบ
            self.ec2_client.describe_regions(MaxResults=1)
            self.logger.info("✅ EC2 service connection successful")
            return True
        except Exception as e:
            self.logger.error(f"❌ EC2 service connection failed: {e}")
            return False
    
    def create_instance(self,
                       image_id: str,
                       instance_type: str,
                       key_name: Optional[str] = None,
                       security_group_ids: Optional[List[str]] = None,
                       subnet_id: Optional[str] = None,
                       user_data: Optional[str] = None,
                       tags: Optional[Dict[str, str]] = None,
                       min_count: int = 1,
                       max_count: int = 1) -> Dict[str, Any]:
        """Create EC2 instance(s)"""
        try:
            launch_config = {
                'ImageId': image_id,
                'MinCount': min_count,
                'MaxCount': max_count,
                'InstanceType': instance_type
            }
            
            if key_name:
                launch_config['KeyName'] = key_name
            if security_group_ids:
                launch_config['SecurityGroupIds'] = security_group_ids
            if subnet_id:
                launch_config['SubnetId'] = subnet_id
            if user_data:
                launch_config['UserData'] = user_data
            
            response = self.ec2_client.run_instances(**launch_config)
            
            # Add tags if provided
            if tags and response.get('Instances'):
                instance_ids = [instance['InstanceId'] for instance in response['Instances']]
                self.add_tags(instance_ids, tags)
            
            logger.info(f"Successfully created {len(response['Instances'])} EC2 instance(s)")
            return response
        
        except Exception as e:
            logger.error(f"Error creating EC2 instance: {str(e)}")
            raise
    
    def start_instance(self, instance_id: str) -> Dict[str, Any]:
        """Start EC2 instance"""
        try:
            response = self.ec2_client.start_instances(InstanceIds=[instance_id])
            logger.info(f"Successfully started EC2 instance: {instance_id}")
            return response
        
        except Exception as e:
            logger.error(f"Error starting EC2 instance {instance_id}: {str(e)}")
            raise
    
    def stop_instance(self, instance_id: str, force: bool = False) -> Dict[str, Any]:
        """Stop EC2 instance"""
        try:
            response = self.ec2_client.stop_instances(
                InstanceIds=[instance_id],
                Force=force
            )
            logger.info(f"Successfully stopped EC2 instance: {instance_id}")
            return response
        
        except Exception as e:
            logger.error(f"Error stopping EC2 instance {instance_id}: {str(e)}")
            raise
    
    def terminate_instance(self, instance_id: str) -> Dict[str, Any]:
        """Terminate EC2 instance"""
        try:
            response = self.ec2_client.terminate_instances(InstanceIds=[instance_id])
            logger.info(f"Successfully terminated EC2 instance: {instance_id}")
            return response
        
        except Exception as e:
            logger.error(f"Error terminating EC2 instance {instance_id}: {str(e)}")
            raise
    
    def reboot_instance(self, instance_id: str) -> Dict[str, Any]:
        """Reboot EC2 instance"""
        try:
            response = self.ec2_client.reboot_instances(InstanceIds=[instance_id])
            logger.info(f"Successfully rebooted EC2 instance: {instance_id}")
            return response
        
        except Exception as e:
            logger.error(f"Error rebooting EC2 instance {instance_id}: {str(e)}")
            raise
    
    def describe_instances(self, instance_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Describe EC2 instances"""
        try:
            if instance_ids:
                response = self.ec2_client.describe_instances(InstanceIds=instance_ids)
            else:
                response = self.ec2_client.describe_instances()
            
            instances = []
            for reservation in response['Reservations']:
                instances.extend(reservation['Instances'])
            
            logger.info(f"Found {len(instances)} EC2 instance(s)")
            return instances
        
        except Exception as e:
            logger.error(f"Error describing EC2 instances: {str(e)}")
            raise
    
    def get_instance_status(self, instance_id: str) -> Dict[str, Any]:
        """Get EC2 instance status"""
        try:
            response = self.ec2_client.describe_instance_status(
                InstanceIds=[instance_id],
                IncludeAllInstances=True
            )
            
            if response['InstanceStatuses']:
                status = response['InstanceStatuses'][0]
                logger.info(f"Retrieved status for EC2 instance: {instance_id}")
                return status
            else:
                logger.warning(f"No status found for EC2 instance: {instance_id}")
                return {}
        
        except Exception as e:
            logger.error(f"Error getting EC2 instance status {instance_id}: {str(e)}")
            raise
    
    def create_security_group(self, 
                             group_name: str,
                             description: str,
                             vpc_id: Optional[str] = None,
                             tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create security group"""
        try:
            create_config = {
                'GroupName': group_name,
                'Description': description
            }
            
            if vpc_id:
                create_config['VpcId'] = vpc_id
            
            response = self.ec2_client.create_security_group(**create_config)
            group_id = response['GroupId']
            
            if tags:
                self.add_tags([group_id], tags)
            
            logger.info(f"Successfully created security group: {group_name} ({group_id})")
            return response
        
        except Exception as e:
            logger.error(f"Error creating security group {group_name}: {str(e)}")
            raise
    
    def authorize_security_group_ingress(self,
                                       group_id: str,
                                       ip_protocol: str,
                                       from_port: int,
                                       to_port: int,
                                       cidr_ip: str = "0.0.0.0/0") -> Dict[str, Any]:
        """Add inbound rule to security group"""
        try:
            response = self.ec2_client.authorize_security_group_ingress(
                GroupId=group_id,
                IpPermissions=[
                    {
                        'IpProtocol': ip_protocol,
                        'FromPort': from_port,
                        'ToPort': to_port,
                        'IpRanges': [{'CidrIp': cidr_ip}]
                    }
                ]
            )
            logger.info(f"Successfully added ingress rule to security group: {group_id}")
            return response
        
        except Exception as e:
            logger.error(f"Error adding ingress rule to security group {group_id}: {str(e)}")
            raise
    
    def create_key_pair(self, key_name: str) -> Dict[str, Any]:
        """Create EC2 key pair"""
        try:
            response = self.ec2_client.create_key_pair(KeyName=key_name)
            logger.info(f"Successfully created key pair: {key_name}")
            return response
        
        except Exception as e:
            logger.error(f"Error creating key pair {key_name}: {str(e)}")
            raise
    
    def delete_key_pair(self, key_name: str) -> Dict[str, Any]:
        """Delete EC2 key pair"""
        try:
            response = self.ec2_client.delete_key_pair(KeyName=key_name)
            logger.info(f"Successfully deleted key pair: {key_name}")
            return response
        
        except Exception as e:
            logger.error(f"Error deleting key pair {key_name}: {str(e)}")
            raise
    
    def add_tags(self, resource_ids: List[str], tags: Dict[str, str]) -> Dict[str, Any]:
        """Add tags to EC2 resources"""
        try:
            tag_list = [{'Key': key, 'Value': value} for key, value in tags.items()]
            response = self.ec2_client.create_tags(
                Resources=resource_ids,
                Tags=tag_list
            )
            logger.info(f"Successfully added tags to resources: {resource_ids}")
            return response
        
        except Exception as e:
            logger.error(f"Error adding tags to resources {resource_ids}: {str(e)}")
            raise
    
    def create_snapshot(self, 
                       volume_id: str,
                       description: str,
                       tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create EBS snapshot"""
        try:
            response = self.ec2_client.create_snapshot(
                VolumeId=volume_id,
                Description=description
            )
            
            if tags:
                snapshot_id = response['SnapshotId']
                self.add_tags([snapshot_id], tags)
            
            logger.info(f"Successfully created snapshot: {response['SnapshotId']}")
            return response
        
        except Exception as e:
            logger.error(f"Error creating snapshot for volume {volume_id}: {str(e)}")
            raise