# AWS Actions Library

ไลบรารี Python สำหรับจัดการ AWS Services ต่างๆ ผ่าน boto3 พร้อมระบบจัดการ credentials ที่สมบูรณ์

## 🚀 Features หลัก

### ✨ **การจัดการ Credentials อัตโนมัติ**
- Auto-detection ของ AWS credentials
- รองรับ AWS CLI, Environment Variables, IAM Roles, และ Profiles
- Interactive setup สำหรับความสะดวก
- Test connection และ validation

### 🛠️ **Services ที่รองรับ**

#### 1. **AWS Lambda** (`aws_lambda_actions.py`)
- สร้าง, อัพเดต, และลบ Lambda functions
- เรียกใช้ functions และจัดการ permissions
- จัดการ environment variables และ configurations

#### 2. **AWS EC2** (`aws_ec2_actions.py`)  
- สร้าง, เริ่ม, หยุด, และลบ EC2 instances
- จัดการ Security Groups และ Key Pairs
- สร้าง EBS snapshots และจัดการ tags

#### 3. **AWS S3** (`aws_s3_actions.py`)
- สร้างและลบ S3 buckets
- อัพโหลดและดาวน์โหลดไฟล์
- จัดการ bucket policies และ versioning
- สร้าง presigned URLs

#### 4. **AWS ECS** (`aws_ecs_actions.py`)
- สร้างและจัดการ ECS clusters
- สร้าง task definitions และ services
- รัน tasks และติดตามสถานะ
- ดู logs และ monitoring

#### 5. **AWS EKS** (`aws_eks_actions.py`)
- สร้างและจัดการ EKS clusters
- จัดการ node groups และ addons
- อัพเดต cluster และ node group versions
- รอสถานะการทำงาน

#### 6. **AWS Secrets Manager** (`aws_secrets_actions.py`) 🔐
- จัดการ passwords และ secrets
- ระบบ rotation อัตโนมัติ
- Parameter Store integration
- IAM user password management

### 🎯 **Advanced Features**
- **Error Handling**: ระบบจัดการ error ที่ครอบคลุม
- **Logging**: ระบบ logging ที่สมบูรณ์
- **Type Hints**: Type annotations สำหรับ IntelliSense
- **Configuration Management**: จัดการ config แยกตาม environment
- **CLI Interface**: Command line interface สำหรับใช้งานง่าย

## 📦 การติดตั้ง

### **ขั้นตอนที่ 1: ติดตั้ง Dependencies**
```bash
# ติดตั้งจาก requirements.txt
pip install -r requirements.txt

# หรือติดตั้งแยก
pip install boto3 botocore python-dateutil
```

### **ขั้นตอนที่ 2: ตั้งค่า AWS Credentials**

#### **วิธีที่ 1: AWS CLI (แนะนำ) 🌟**
```bash
# ติดตั้ง AWS CLI
pip install awscli

# ตั้งค่า credentials
aws configure
```

#### **วิธีที่ 2: Environment Variables**
```bash
# Windows
set AWS_ACCESS_KEY_ID=your_access_key
set AWS_SECRET_ACCESS_KEY=your_secret_key
set AWS_DEFAULT_REGION=us-east-1

# Linux/Mac
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key  
export AWS_DEFAULT_REGION=us-east-1
```

#### **วิธีที่ 3: Interactive Setup**
```bash
python -c "from aws_credentials import AWSCredentialsManager; AWSCredentialsManager().setup_interactive()"
```

## 🔧 การใช้งาน

### **1. Basic Usage**

```python
from aws_lambda_actions import LambdaActions
from aws_s3_actions import S3Actions
from aws_ec2_actions import EC2Actions

# Auto setup - จะหา credentials อัตโนมัติ
lambda_client = LambdaActions()
s3_client = S3Actions()
ec2_client = EC2Actions()

# ระบุ region และ profile
lambda_client = LambdaActions(
    region_name='ap-southeast-1',
    profile_name='myproject'
)
```

### **2. Credential Management**

```python
from aws_credentials import AWSCredentialsManager
from aws_config import AWSConfig

# ตั้งค่า credentials
credentials_manager = AWSCredentialsManager()

# Auto setup
if credentials_manager.setup_credentials('auto'):
    print("✅ Credentials ready!")

# Interactive setup
credentials_manager.setup_interactive()

# แสดง configuration ปัจจุบัน
AWSConfig.print_current_config()

# ทดสอบการเชื่อมต่อ
credentials_manager.test_connection()
```

### **3. Lambda Examples**

```python
from aws_lambda_actions import LambdaActions

# สร้าง client
lambda_client = LambdaActions()

# สร้าง function
with open('function.zip', 'rb') as f:
    zip_content = f.read()

response = lambda_client.create_function(
    function_name='my-function',
    runtime='python3.9',
    role='arn:aws:iam::123456789012:role/lambda-role',
    handler='lambda_function.lambda_handler',
    zip_file=zip_content,
    timeout=30,
    memory_size=256,
    environment_variables={'ENV': 'production'},
    tags={'Project': 'MyApp'}
)

# เรียกใช้ function
result = lambda_client.invoke_function(
    function_name='my-function',
    payload={'key': 'value'}
)

# ดูรายการ functions
functions = lambda_client.list_functions()
print(f"Found {len(functions)} functions")
```

### **4. EC2 Examples**

```python
from aws_ec2_actions import EC2Actions

# สร้าง client
ec2_client = EC2Actions()

# สร้าง security group
sg_result = ec2_client.create_security_group(
    group_name='web-sg',
    description='Web server security group',
    tags={'Environment': 'Production'}
)

# เพิ่ม inbound rules
ec2_client.authorize_security_group_ingress(
    group_id=sg_result['GroupId'],
    ip_protocol='tcp',
    from_port=80,
    to_port=80,
    cidr_ip='0.0.0.0/0'
)

# สร้าง instance
response = ec2_client.create_instance(
    image_id='ami-0abcdef1234567890',
    instance_type='t3.micro',
    key_name='my-key-pair',
    security_group_ids=[sg_result['GroupId']],
    tags={'Name': 'Web Server', 'Environment': 'Production'}
)

# ดูรายการ instances
instances = ec2_client.describe_instances()
```

### **5. S3 Examples**

```python
from aws_s3_actions import S3Actions

# สร้าง client
s3_client = S3Actions()

# สร้าง bucket
s3_client.create_bucket(
    bucket_name='my-app-bucket-12345',
    region='ap-southeast-1',
    tags={'Project': 'MyApp', 'Environment': 'Production'}
)

# อัพโหลดไฟล์
s3_client.upload_file(
    file_path='/path/to/local/file.txt',
    bucket_name='my-app-bucket-12345',
    object_key='uploads/file.txt'
)

# สร้าง presigned URL
url = s3_client.generate_presigned_url(
    bucket_name='my-app-bucket-12345',
    object_key='uploads/file.txt',
    expiration=3600  # 1 hour
)

# ดูรายการ buckets
buckets = s3_client.list_buckets()
```

### **6. Secrets Manager Examples** 🔐

```python
from aws_secrets_actions import SecretsManagerActions

# สร้าง client
secrets_client = SecretsManagerActions()

# สร้าง database secret
secrets_client.create_database_secret(
    secret_name='prod-db-credentials',
    username='admin',
    password='super-secret-password',
    host='db.example.com',
    port=5432,
    database='production',
    engine='postgresql'
)

# ดึงข้อมูล credentials
credentials = secrets_client.get_database_credentials('prod-db-credentials')
print(f"DB Host: {credentials['host']}")

# สร้าง API key secret
secrets_client.create_api_key_secret(
    secret_name='external-api-key',
    api_key='abc123xyz789',
    service_name='payment-gateway'
)

# Generate random password
password = secrets_client.generate_random_password(
    length=32,
    exclude_characters='@#$%'
)

# Parameter Store
secrets_client.put_parameter(
    name='/myapp/config/api-url',
    value='https://api.example.com',
    secure=False
)
```

## 🖥️ Command Line Interface

```bash
# ตั้งค่า credentials แบบ interactive
python aws_cli.py setup --interactive

# แสดง configuration ปัจจุบัน
python aws_cli.py config

# ทดสอบการเชื่อมต่อ
python aws_cli.py test

# ทดสอบ services เฉพาะ
python aws_cli.py test --services lambda s3 ec2

# ดูรายการ resources
python aws_cli.py list lambda      # Lambda functions
python aws_cli.py list ec2         # EC2 instances
python aws_cli.py list s3          # S3 buckets
python aws_cli.py list ecs         # ECS clusters
python aws_cli.py list eks         # EKS clusters
```

## 📁 โครงสร้างไฟล์

```
aws_utils/
├── __init__.py                     # Package initialization
├── aws_credentials.py              # Credential management
├── aws_config.py                  # Configuration management
├── aws_lambda_actions.py           # Lambda functions
├── aws_ec2_actions.py             # EC2 instances & resources  
├── aws_s3_actions.py              # S3 buckets & objects
├── aws_ecs_actions.py             # ECS clusters & services
├── aws_eks_actions.py             # EKS clusters & node groups
├── aws_secrets_actions.py         # Secrets & password management
├── aws_cli.py                     # Command line interface
├── examples.py                    # ตัวอย่างการใช้งาน
├── requirements.txt               # Dependencies
└── README.md                     # เอกสารนี้
```

## 🎮 Interactive Examples

```bash
# รัน examples แบบ interactive
python examples.py --interactive

# รัน examples ทั้งหมด
python examples.py

# ตั้งค่า credentials
python examples.py --setup

# ดู configuration
python examples.py --config

# ทดสอบ services
python examples.py --test
```

## 🛡️ Security Best Practices

### **1. Credential Security**
```python
# ❌ ไม่ควรทำ - hardcode credentials
lambda_client = LambdaActions(access_key="AKIAXXXXX", secret_key="xxxxx")

# ✅ ควรทำ - ใช้ credential management
lambda_client = LambdaActions()  # Auto-detect credentials
```

### **2. IAM Permissions**
สร้าง IAM policy ที่มี permissions เฉพาะที่จำเป็น:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "lambda:ListFunctions",
                "lambda:GetFunction",
                "lambda:InvokeFunction",
                "s3:ListBucket",
                "s3:GetObject",
                "s3:PutObject",
                "ec2:DescribeInstances",
                "secretsmanager:GetSecretValue"
            ],
            "Resource": "*"
        }
    ]
}
```

### **3. Environment Variables**
```bash
# ตั้งค่า environment variables อย่างปลอดภัย
export AWS_ACCESS_KEY_ID="your_key"
export AWS_SECRET_ACCESS_KEY="your_secret"
export AWS_DEFAULT_REGION="us-east-1"

# อย่าเก็บใน version control
echo "*.env" >> .gitignore
```

## 🔍 Troubleshooting

### **Common Issues**

#### **1. No credentials found**
```python
# ตรวจสอบ credentials
from aws_credentials import AWSCredentialsManager

credentials_manager = AWSCredentialsManager()
if not credentials_manager.setup_credentials('auto'):
    print("Please configure AWS credentials")
    credentials_manager.setup_interactive()
```

#### **2. Access denied**
```python
# ตรวจสอบ permissions
try:
    lambda_client = LambdaActions()
    functions = lambda_client.list_functions()
except Exception as e:
    print(f"Permission error: {e}")
    print("Check your IAM permissions")
```

#### **3. Wrong region**
```python
# ระบุ region ที่ถูกต้อง
lambda_client = LambdaActions(region_name='ap-southeast-1')

# หรือตั้งค่าใน environment
os.environ['AWS_DEFAULT_REGION'] = 'ap-southeast-1'
```

## 📊 Monitoring และ Logging

```python
import logging

# ตั้งค่า logging level
logging.basicConfig(level=logging.INFO)

# ดู logs ของ AWS actions
logger = logging.getLogger('aws_lambda_actions')
logger.setLevel(logging.DEBUG)

# ใช้งานพร้อม logging
lambda_client = LambdaActions()
functions = lambda_client.list_functions()  # จะมี logs แสดง
```

## 🚀 Advanced Usage

### **1. Multiple Regions**
```python
# ใช้หลาย regions พร้อมกัน
regions = ['us-east-1', 'ap-southeast-1', 'eu-west-1']

for region in regions:
    lambda_client = LambdaActions(region_name=region)
    functions = lambda_client.list_functions()
    print(f"{region}: {len(functions)} functions")
```

### **2. Multiple Profiles**
```python
# ใช้หลาย AWS profiles
profiles = ['default', 'production', 'development']

for profile in profiles:
    try:
        lambda_client = LambdaActions(profile_name=profile)
        identity = lambda_client.get_current_identity()
        print(f"{profile}: {identity.get('Account')}")
    except Exception as e:
        print(f"{profile}: Error - {e}")
```

### **3. Batch Operations**
```python
# จัดการ multiple resources
from concurrent.futures import ThreadPoolExecutor

def stop_instance(instance_id):
    ec2_client = EC2Actions()
    return ec2_client.stop_instance(instance_id)

# Stop หลาย instances พร้อมกัน
instance_ids = ['i-1234567890abcdef0', 'i-0987654321fedcba0']

with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(stop_instance, instance_ids))
```

## 📝 ข้อควรระวัง

1. **💰 Costs**: การใช้ AWS services อาจมีค่าใช้จ่าย
2. **🔐 Security**: ไม่ควร hardcode credentials ในโค้ด
3. **⚡ Rate Limits**: AWS มี API rate limits ที่ต้องคำนึงถึง
4. **🌍 Regions**: ตรวจสอบให้แน่ใจว่าใช้ region ที่ถูกต้อง
5. **📋 Permissions**: ตรวจสอบ IAM permissions ที่เพียงพอ

## 📚 เพิ่มเติม

- 📖 [AWS SDK Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- 🔧 [AWS CLI Configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html)
- 🛡️ [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- 💡 [AWS Free Tier](https://aws.amazon.com/free/)

## 📄 License

MIT License - ใช้งานได้อย่างอิสระ

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Create Pull Request

---

💡 **Tip**: ใช้ `python examples.py --interactive` เพื่อเริ่มต้นและทดลองใช้งานได้ทันที! 🚀