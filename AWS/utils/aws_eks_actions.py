import boto3
import json
import logging
from typing import Dict, Any, Optional, List
from .aws_credentials import AWSCredentialsManager
from .aws_config import AWSConfig

logger = logging.getLogger(__name__)

class EKSActions:
    """AWS EKS actions handler with improved credential management"""
    
    def __init__(self, region_name: str = None, profile_name: str = None, auto_setup: bool = True):
        # Get configuration
        config = AWSConfig.get_service_config('eks')
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
            self.eks_client = self.session.client('eks')
            self.ec2_client = self.session.client('ec2')
            
            # ทดสอบการเชื่อมต่อ
            if not self.credentials_manager.test_connection(region_name=self.region_name):
                raise Exception("Failed to connect to AWS")
                
            self.logger.info(f"✅ EKS client initialized successfully in region: {self.region_name}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup EKS client: {e}")
            self.logger.info("💡 Please configure AWS credentials first")
            raise
    
    def test_connection(self) -> bool:
        """ทดสอบการเชื่อมต่อ EKS service"""
        try:
            # ลองเรียก list_clusters เพื่อทดสอบ
            self.eks_client.list_clusters(maxResults=1)
            self.logger.info("✅ EKS service connection successful")
            return True
        except Exception as e:
            self.logger.error(f"❌ EKS service connection failed: {e}")
            return False
    
    def create_cluster(self,
                      name: str,
                      version: str,
                      role_arn: str,
                      resources_vpc_config: Dict[str, Any],
                      logging: Optional[Dict[str, Any]] = None,
                      client_request_token: Optional[str] = None,
                      tags: Optional[Dict[str, str]] = None,
                      encryption_config: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Create EKS cluster"""
        try:
            create_config = {
                'name': name,
                'version': version,
                'roleArn': role_arn,
                'resourcesVpcConfig': resources_vpc_config
            }
            
            if logging:
                create_config['logging'] = logging
            if client_request_token:
                create_config['clientRequestToken'] = client_request_token
            if tags:
                create_config['tags'] = tags
            if encryption_config:
                create_config['encryptionConfig'] = encryption_config
            
            response = self.eks_client.create_cluster(**create_config)
            logger.info(f"Successfully created EKS cluster: {name}")
            return response
        
        except Exception as e:
            logger.error(f"Error creating EKS cluster {name}: {str(e)}")
            raise
    
    def delete_cluster(self, name: str) -> Dict[str, Any]:
        """Delete EKS cluster"""
        try:
            response = self.eks_client.delete_cluster(name=name)
            logger.info(f"Successfully deleted EKS cluster: {name}")
            return response
        
        except Exception as e:
            logger.error(f"Error deleting EKS cluster {name}: {str(e)}")
            raise
    
    def describe_cluster(self, name: str) -> Dict[str, Any]:
        """Describe EKS cluster"""
        try:
            response = self.eks_client.describe_cluster(name=name)
            logger.info(f"Successfully described EKS cluster: {name}")
            return response
        
        except Exception as e:
            logger.error(f"Error describing EKS cluster {name}: {str(e)}")
            raise
    
    def list_clusters(self) -> List[str]:
        """List EKS clusters"""
        try:
            response = self.eks_client.list_clusters()
            clusters = response.get('clusters', [])
            logger.info(f"Found {len(clusters)} EKS clusters")
            return clusters
        
        except Exception as e:
            logger.error(f"Error listing EKS clusters: {str(e)}")
            raise
    
    def update_cluster_version(self, name: str, version: str) -> Dict[str, Any]:
        """Update EKS cluster version"""
        try:
            response = self.eks_client.update_cluster_version(
                name=name,
                version=version
            )
            logger.info(f"Successfully updated EKS cluster version: {name} to {version}")
            return response
        
        except Exception as e:
            logger.error(f"Error updating EKS cluster version {name}: {str(e)}")
            raise
    
    def update_cluster_config(self,
                             name: str,
                             resources_vpc_config: Optional[Dict[str, Any]] = None,
                             logging: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Update EKS cluster configuration"""
        try:
            update_config = {'name': name}
            
            if resources_vpc_config:
                update_config['resourcesVpcConfig'] = resources_vpc_config
            if logging:
                update_config['logging'] = logging
            
            response = self.eks_client.update_cluster_config(**update_config)
            logger.info(f"Successfully updated EKS cluster config: {name}")
            return response
        
        except Exception as e:
            logger.error(f"Error updating EKS cluster config {name}: {str(e)}")
            raise
    
    def create_nodegroup(self,
                        cluster_name: str,
                        nodegroup_name: str,
                        subnets: List[str],
                        node_role: str,
                        instance_types: List[str],
                        ami_type: Optional[str] = None,
                        capacity_type: Optional[str] = None,
                        scaling_config: Optional[Dict[str, Any]] = None,
                        disk_size: Optional[int] = None,
                        remote_access: Optional[Dict[str, Any]] = None,
                        labels: Optional[Dict[str, str]] = None,
                        tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create EKS node group"""
        try:
            create_config = {
                'clusterName': cluster_name,
                'nodegroupName': nodegroup_name,
                'subnets': subnets,
                'nodeRole': node_role,
                'instanceTypes': instance_types
            }
            
            if ami_type:
                create_config['amiType'] = ami_type
            if capacity_type:
                create_config['capacityType'] = capacity_type
            if scaling_config:
                create_config['scalingConfig'] = scaling_config
            if disk_size:
                create_config['diskSize'] = disk_size
            if remote_access:
                create_config['remoteAccess'] = remote_access
            if labels:
                create_config['labels'] = labels
            if tags:
                create_config['tags'] = tags
            
            response = self.eks_client.create_nodegroup(**create_config)
            logger.info(f"Successfully created EKS node group: {nodegroup_name}")
            return response
        
        except Exception as e:
            logger.error(f"Error creating EKS node group {nodegroup_name}: {str(e)}")
            raise
    
    def delete_nodegroup(self, cluster_name: str, nodegroup_name: str) -> Dict[str, Any]:
        """Delete EKS node group"""
        try:
            response = self.eks_client.delete_nodegroup(
                clusterName=cluster_name,
                nodegroupName=nodegroup_name
            )
            logger.info(f"Successfully deleted EKS node group: {nodegroup_name}")
            return response
        
        except Exception as e:
            logger.error(f"Error deleting EKS node group {nodegroup_name}: {str(e)}")
            raise
    
    def describe_nodegroup(self, cluster_name: str, nodegroup_name: str) -> Dict[str, Any]:
        """Describe EKS node group"""
        try:
            response = self.eks_client.describe_nodegroup(
                clusterName=cluster_name,
                nodegroupName=nodegroup_name
            )
            logger.info(f"Successfully described EKS node group: {nodegroup_name}")
            return response
        
        except Exception as e:
            logger.error(f"Error describing EKS node group {nodegroup_name}: {str(e)}")
            raise
    
    def list_nodegroups(self, cluster_name: str) -> List[str]:
        """List EKS node groups"""
        try:
            response = self.eks_client.list_nodegroups(clusterName=cluster_name)
            nodegroups = response.get('nodegroups', [])
            logger.info(f"Found {len(nodegroups)} EKS node groups in cluster {cluster_name}")
            return nodegroups
        
        except Exception as e:
            logger.error(f"Error listing EKS node groups for cluster {cluster_name}: {str(e)}")
            raise
    
    def update_nodegroup_config(self,
                               cluster_name: str,
                               nodegroup_name: str,
                               labels: Optional[Dict[str, str]] = None,
                               scaling_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Update EKS node group configuration"""
        try:
            update_config = {
                'clusterName': cluster_name,
                'nodegroupName': nodegroup_name
            }
            
            if labels:
                update_config['labels'] = {'addOrUpdateLabels': labels}
            if scaling_config:
                update_config['scalingConfig'] = scaling_config
            
            response = self.eks_client.update_nodegroup_config(**update_config)
            logger.info(f"Successfully updated EKS node group config: {nodegroup_name}")
            return response
        
        except Exception as e:
            logger.error(f"Error updating EKS node group config {nodegroup_name}: {str(e)}")
            raise
    
    def update_nodegroup_version(self,
                                cluster_name: str,
                                nodegroup_name: str,
                                version: Optional[str] = None,
                                release_version: Optional[str] = None,
                                force: bool = False) -> Dict[str, Any]:
        """Update EKS node group version"""
        try:
            update_config = {
                'clusterName': cluster_name,
                'nodegroupName': nodegroup_name,
                'force': force
            }
            
            if version:
                update_config['version'] = version
            if release_version:
                update_config['releaseVersion'] = release_version
            
            response = self.eks_client.update_nodegroup_version(**update_config)
            logger.info(f"Successfully updated EKS node group version: {nodegroup_name}")
            return response
        
        except Exception as e:
            logger.error(f"Error updating EKS node group version {nodegroup_name}: {str(e)}")
            raise
    
    def create_addon(self,
                    cluster_name: str,
                    addon_name: str,
                    addon_version: Optional[str] = None,
                    service_account_role_arn: Optional[str] = None,
                    resolve_conflicts: str = 'OVERWRITE',
                    tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create EKS addon"""
        try:
            create_config = {
                'clusterName': cluster_name,
                'addonName': addon_name,
                'resolveConflicts': resolve_conflicts
            }
            
            if addon_version:
                create_config['addonVersion'] = addon_version
            if service_account_role_arn:
                create_config['serviceAccountRoleArn'] = service_account_role_arn
            if tags:
                create_config['tags'] = tags
            
            response = self.eks_client.create_addon(**create_config)
            logger.info(f"Successfully created EKS addon: {addon_name}")
            return response
        
        except Exception as e:
            logger.error(f"Error creating EKS addon {addon_name}: {str(e)}")
            raise
    
    def delete_addon(self, cluster_name: str, addon_name: str) -> Dict[str, Any]:
        """Delete EKS addon"""
        try:
            response = self.eks_client.delete_addon(
                clusterName=cluster_name,
                addonName=addon_name
            )
            logger.info(f"Successfully deleted EKS addon: {addon_name}")
            return response
        
        except Exception as e:
            logger.error(f"Error deleting EKS addon {addon_name}: {str(e)}")
            raise
    
    def list_addons(self, cluster_name: str) -> List[str]:
        """List EKS addons"""
        try:
            response = self.eks_client.list_addons(clusterName=cluster_name)
            addons = response.get('addons', [])
            logger.info(f"Found {len(addons)} EKS addons in cluster {cluster_name}")
            return addons
        
        except Exception as e:
            logger.error(f"Error listing EKS addons for cluster {cluster_name}: {str(e)}")
            raise
    
    def describe_addon(self, cluster_name: str, addon_name: str) -> Dict[str, Any]:
        """Describe EKS addon"""
        try:
            response = self.eks_client.describe_addon(
                clusterName=cluster_name,
                addonName=addon_name
            )
            logger.info(f"Successfully described EKS addon: {addon_name}")
            return response
        
        except Exception as e:
            logger.error(f"Error describing EKS addon {addon_name}: {str(e)}")
            raise
    
    def get_cluster_status(self, cluster_name: str) -> str:
        """Get EKS cluster status"""
        try:
            response = self.describe_cluster(cluster_name)
            status = response['cluster']['status']
            logger.info(f"EKS cluster {cluster_name} status: {status}")
            return status
        
        except Exception as e:
            logger.error(f"Error getting EKS cluster status {cluster_name}: {str(e)}")
            raise
    
    def wait_for_cluster_active(self, cluster_name: str, max_attempts: int = 40) -> bool:
        """Wait for EKS cluster to become active"""
        try:
            waiter = self.eks_client.get_waiter('cluster_active')
            waiter.wait(
                name=cluster_name,
                WaiterConfig={'MaxAttempts': max_attempts}
            )
            logger.info(f"EKS cluster {cluster_name} is now active")
            return True
        
        except Exception as e:
            logger.error(f"Error waiting for EKS cluster {cluster_name} to become active: {str(e)}")
            raise
    
    def wait_for_nodegroup_active(self, cluster_name: str, nodegroup_name: str, max_attempts: int = 40) -> bool:
        """Wait for EKS node group to become active"""
        try:
            waiter = self.eks_client.get_waiter('nodegroup_active')
            waiter.wait(
                clusterName=cluster_name,
                nodegroupName=nodegroup_name,
                WaiterConfig={'MaxAttempts': max_attempts}
            )
            logger.info(f"EKS node group {nodegroup_name} is now active")
            return True
        
        except Exception as e:
            logger.error(f"Error waiting for EKS node group {nodegroup_name} to become active: {str(e)}")
            raise