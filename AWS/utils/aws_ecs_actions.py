import boto3
import json
import logging
from typing import Dict, Any, Optional, List
from .aws_credentials import AWSCredentialsManager
from .aws_config import AWSConfig

logger = logging.getLogger(__name__)

class ECSActions:
    """AWS ECS actions handler with improved credential management"""
    
    def __init__(self, region_name: str = None, profile_name: str = None, auto_setup: bool = True):
        # Get configuration
        config = AWSConfig.get_service_config('ecs')
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
            self.ecs_client = self.session.client('ecs')
            
            # ทดสอบการเชื่อมต่อ
            if not self.credentials_manager.test_connection(region_name=self.region_name):
                raise Exception("Failed to connect to AWS")
                
            self.logger.info(f"✅ ECS client initialized successfully in region: {self.region_name}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup ECS client: {e}")
            self.logger.info("💡 Please configure AWS credentials first")
            raise
    
    def test_connection(self) -> bool:
        """ทดสอบการเชื่อมต่อ ECS service"""
        try:
            # ลองเรียก list_clusters เพื่อทดสอบ
            self.ecs_client.list_clusters(maxResults=1)
            self.logger.info("✅ ECS service connection successful")
            return True
        except Exception as e:
            self.logger.error(f"❌ ECS service connection failed: {e}")
            return False
    
    def create_cluster(self, 
                      cluster_name: str,
                      capacity_providers: Optional[List[str]] = None,
                      tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create ECS cluster"""
        try:
            create_config = {'clusterName': cluster_name}
            
            if capacity_providers:
                create_config['capacityProviders'] = capacity_providers
            
            if tags:
                tag_list = [{'key': key, 'value': value} for key, value in tags.items()]
                create_config['tags'] = tag_list
            
            response = self.ecs_client.create_cluster(**create_config)
            logger.info(f"Successfully created ECS cluster: {cluster_name}")
            return response
        
        except Exception as e:
            logger.error(f"Error creating ECS cluster {cluster_name}: {str(e)}")
            raise
    
    def delete_cluster(self, cluster_name: str) -> Dict[str, Any]:
        """Delete ECS cluster"""
        try:
            response = self.ecs_client.delete_cluster(cluster=cluster_name)
            logger.info(f"Successfully deleted ECS cluster: {cluster_name}")
            return response
        
        except Exception as e:
            logger.error(f"Error deleting ECS cluster {cluster_name}: {str(e)}")
            raise
    
    def create_task_definition(self,
                              family: str,
                              container_definitions: List[Dict[str, Any]],
                              task_role_arn: Optional[str] = None,
                              execution_role_arn: Optional[str] = None,
                              network_mode: str = 'awsvpc',
                              requires_compatibility: List[str] = None,
                              cpu: Optional[str] = None,
                              memory: Optional[str] = None,
                              tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create ECS task definition"""
        try:
            task_def_config = {
                'family': family,
                'containerDefinitions': container_definitions,
                'networkMode': network_mode
            }
            
            if task_role_arn:
                task_def_config['taskRoleArn'] = task_role_arn
            if execution_role_arn:
                task_def_config['executionRoleArn'] = execution_role_arn
            if requires_compatibility:
                task_def_config['requiresCompatibilities'] = requires_compatibility
            if cpu:
                task_def_config['cpu'] = cpu
            if memory:
                task_def_config['memory'] = memory
            if tags:
                tag_list = [{'key': key, 'value': value} for key, value in tags.items()]
                task_def_config['tags'] = tag_list
            
            response = self.ecs_client.register_task_definition(**task_def_config)
            logger.info(f"Successfully created ECS task definition: {family}")
            return response
        
        except Exception as e:
            logger.error(f"Error creating ECS task definition {family}: {str(e)}")
            raise
    
    def create_service(self,
                      service_name: str,
                      cluster: str,
                      task_definition: str,
                      desired_count: int = 1,
                      launch_type: str = 'FARGATE',
                      network_configuration: Optional[Dict[str, Any]] = None,
                      load_balancers: Optional[List[Dict[str, Any]]] = None,
                      service_registries: Optional[List[Dict[str, Any]]] = None,
                      tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create ECS service"""
        try:
            service_config = {
                'serviceName': service_name,
                'cluster': cluster,
                'taskDefinition': task_definition,
                'desiredCount': desired_count,
                'launchType': launch_type
            }
            
            if network_configuration:
                service_config['networkConfiguration'] = network_configuration
            if load_balancers:
                service_config['loadBalancers'] = load_balancers
            if service_registries:
                service_config['serviceRegistries'] = service_registries
            if tags:
                tag_list = [{'key': key, 'value': value} for key, value in tags.items()]
                service_config['tags'] = tag_list
            
            response = self.ecs_client.create_service(**service_config)
            logger.info(f"Successfully created ECS service: {service_name}")
            return response
        
        except Exception as e:
            logger.error(f"Error creating ECS service {service_name}: {str(e)}")
            raise
    
    def update_service(self,
                      service: str,
                      cluster: str,
                      desired_count: Optional[int] = None,
                      task_definition: Optional[str] = None) -> Dict[str, Any]:
        """Update ECS service"""
        try:
            update_config = {
                'service': service,
                'cluster': cluster
            }
            
            if desired_count is not None:
                update_config['desiredCount'] = desired_count
            if task_definition:
                update_config['taskDefinition'] = task_definition
            
            response = self.ecs_client.update_service(**update_config)
            logger.info(f"Successfully updated ECS service: {service}")
            return response
        
        except Exception as e:
            logger.error(f"Error updating ECS service {service}: {str(e)}")
            raise
    
    def delete_service(self, service: str, cluster: str, force: bool = False) -> Dict[str, Any]:
        """Delete ECS service"""
        try:
            # Scale down to 0 first if force is True
            if force:
                self.update_service(service, cluster, desired_count=0)
            
            response = self.ecs_client.delete_service(
                service=service,
                cluster=cluster,
                force=force
            )
            logger.info(f"Successfully deleted ECS service: {service}")
            return response
        
        except Exception as e:
            logger.error(f"Error deleting ECS service {service}: {str(e)}")
            raise
    
    def run_task(self,
                cluster: str,
                task_definition: str,
                count: int = 1,
                launch_type: str = 'FARGATE',
                network_configuration: Optional[Dict[str, Any]] = None,
                overrides: Optional[Dict[str, Any]] = None,
                tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Run ECS task"""
        try:
            run_config = {
                'cluster': cluster,
                'taskDefinition': task_definition,
                'count': count,
                'launchType': launch_type
            }
            
            if network_configuration:
                run_config['networkConfiguration'] = network_configuration
            if overrides:
                run_config['overrides'] = overrides
            if tags:
                tag_list = [{'key': key, 'value': value} for key, value in tags.items()]
                run_config['tags'] = tag_list
            
            response = self.ecs_client.run_task(**run_config)
            logger.info(f"Successfully ran ECS task: {task_definition}")
            return response
        
        except Exception as e:
            logger.error(f"Error running ECS task {task_definition}: {str(e)}")
            raise
    
    def stop_task(self, cluster: str, task_arn: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """Stop ECS task"""
        try:
            stop_config = {
                'cluster': cluster,
                'task': task_arn
            }
            
            if reason:
                stop_config['reason'] = reason
            
            response = self.ecs_client.stop_task(**stop_config)
            logger.info(f"Successfully stopped ECS task: {task_arn}")
            return response
        
        except Exception as e:
            logger.error(f"Error stopping ECS task {task_arn}: {str(e)}")
            raise
    
    def list_clusters(self) -> List[Dict[str, Any]]:
        """List ECS clusters"""
        try:
            response = self.ecs_client.list_clusters()
            cluster_arns = response.get('clusterArns', [])
            
            if cluster_arns:
                # Get detailed information about clusters
                describe_response = self.ecs_client.describe_clusters(clusters=cluster_arns)
                clusters = describe_response.get('clusters', [])
            else:
                clusters = []
            
            logger.info(f"Found {len(clusters)} ECS clusters")
            return clusters
        
        except Exception as e:
            logger.error(f"Error listing ECS clusters: {str(e)}")
            raise
    
    def list_services(self, cluster: str) -> List[Dict[str, Any]]:
        """List ECS services in a cluster"""
        try:
            response = self.ecs_client.list_services(cluster=cluster)
            service_arns = response.get('serviceArns', [])
            
            if service_arns:
                # Get detailed information about services
                describe_response = self.ecs_client.describe_services(
                    cluster=cluster,
                    services=service_arns
                )
                services = describe_response.get('services', [])
            else:
                services = []
            
            logger.info(f"Found {len(services)} ECS services in cluster {cluster}")
            return services
        
        except Exception as e:
            logger.error(f"Error listing ECS services in cluster {cluster}: {str(e)}")
            raise
    
    def list_tasks(self, cluster: str, service_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """List ECS tasks in a cluster"""
        try:
            list_config = {'cluster': cluster}
            if service_name:
                list_config['serviceName'] = service_name
            
            response = self.ecs_client.list_tasks(**list_config)
            task_arns = response.get('taskArns', [])
            
            if task_arns:
                # Get detailed information about tasks
                describe_response = self.ecs_client.describe_tasks(
                    cluster=cluster,
                    tasks=task_arns
                )
                tasks = describe_response.get('tasks', [])
            else:
                tasks = []
            
            logger.info(f"Found {len(tasks)} ECS tasks in cluster {cluster}")
            return tasks
        
        except Exception as e:
            logger.error(f"Error listing ECS tasks in cluster {cluster}: {str(e)}")
            raise
    
    def get_service_logs(self, cluster: str, service: str) -> Dict[str, Any]:
        """Get logs for ECS service tasks"""
        try:
            # First, get the tasks for the service
            tasks = self.list_tasks(cluster, service)
            
            logs_info = {
                'cluster': cluster,
                'service': service,
                'tasks': []
            }
            
            for task in tasks:
                task_arn = task['taskArn']
                task_definition = task['taskDefinitionArn']
                
                logs_info['tasks'].append({
                    'taskArn': task_arn,
                    'taskDefinition': task_definition,
                    'lastStatus': task.get('lastStatus'),
                    'healthStatus': task.get('healthStatus'),
                    'containers': task.get('containers', [])
                })
            
            logger.info(f"Retrieved logs information for ECS service: {service}")
            return logs_info
        
        except Exception as e:
            logger.error(f"Error getting logs for ECS service {service}: {str(e)}")
            raise