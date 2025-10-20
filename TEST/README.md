# Testing and Development Tools

## ภาพรวม
เครื่องมือต่างๆ สำหรับการทดสอบและพัฒนา รวมถึงการเข้ารหัส GPG

## ไฟล์

### test.py
**วัตถุประสงค์**: ไฟล์ทดสอบทั่วไปสำหรับการ development และ debugging

**การใช้งาน**:
- ทดสอบ functions ใหม่
- Prototype development
- Quick testing และ experimentation

### gpg.py
**วัตถุประสงค์**: เครื่องมือสำหรับการเข้ารหัสและถอดรหัสด้วย GPG (GNU Privacy Guard)

**คุณสมบัติ**:
- การเข้ารหัสไฟล์และข้อความ
- การถอดรหัสข้อมูลที่เข้ารหัสแล้ว
- การจัดการ GPG keys
- การ verify digital signatures

**ตัวอย่างการใช้งาน**:
```python
# การเข้ารหัสไฟล์
encrypt_file("document.txt", "recipient@example.com")

# การถอดรหัส
decrypt_file("document.txt.gpg", "output.txt")

# การสร้าง digital signature
sign_file("document.txt")
```

### gpg_gen.py
**วัตถุประสงค์**: เครื่องมือสำหรับสร้าง GPG keys และจัดการ key pairs

**คุณสมบัติ**:
- สร้าง GPG key pairs (public/private keys)
- การ export และ import keys
- การจัดการ key database
- การตั้งค่า key properties (expiration, key size, etc.)

**ตัวอย่างการใช้งาน**:
```python
# สร้าง GPG key pair ใหม่
generate_key_pair(
    name="John Doe",
    email="john@example.com", 
    comment="My GPG Key",
    key_type="RSA",
    key_length=4096,
    expire_date="2025-12-31"
)

# Export public key
export_public_key("john@example.com", "john_public.asc")

# Export private key
export_private_key("john@example.com", "john_private.asc")
```

### Auth.json
**วัตถุประสงค์**: ไฟล์การตั้งค่าการยืนยันตัวตนสำหรับการทดสอบ

**โครงสร้าง**:
```json
{
  "username": "test_user",
  "password": "test_password", 
  "api_key": "your_api_key",
  "endpoints": {
    "login": "https://api.example.com/login",
    "refresh": "https://api.example.com/refresh"
  }
}
```

### SC1.bat
**วัตถุประสงค์**: Batch script สำหรับ Windows automation

**การใช้งาน**:
- การรัน automated tasks บน Windows
- การตั้งค่า environment variables
- การ execute ลำดับ commands

## วิธีใช้งาน

### 1. การตั้งค่า GPG
```bash
# ติดตั้ง GPG (Windows)
# ดาวน์โหลด Gpg4win จาก https://gpg4win.org/

# ติดตั้ง Python GPG library
pip install python-gnupg
```

### 2. การใช้งาน GPG Tools
```python
# Import GPG module
import gnupg

# สร้าง GPG instance
gpg = gnupg.GPG()

# ใช้งานผ่าน custom functions
from gpg import encrypt_file, decrypt_file
from gpg_gen import generate_key_pair
```

### 3. การรัน Batch Script
```cmd
# รัน SC1.bat
SC1.bat

# หรือเรียกใช้จาก Python
import subprocess
subprocess.run(["SC1.bat"], shell=True)
```

### 4. การใช้งาน Auth Config
```python
import json

# โหลด authentication config
with open('Auth.json', 'r') as f:
    auth_config = json.load(f)

username = auth_config['username']
password = auth_config['password']
api_key = auth_config['api_key']
```

## ตัวอย่าง Use Cases

### 1. การเข้ารหัสข้อมูลสำคัญ
```python
from gpg import encrypt_file
from gpg_gen import generate_key_pair

# สร้าง key pair สำหรับการเข้ารหัส
generate_key_pair("Admin", "admin@company.com")

# เข้ารหัสไฟล์ sensitive data
encrypt_file("sensitive_data.txt", "admin@company.com")
```

### 2. การทดสอบ API Authentication
```python
import json
import requests

# โหลด auth config
with open('Auth.json', 'r') as f:
    config = json.load(f)

# ทดสอบการ login
response = requests.post(
    config['endpoints']['login'],
    json={'username': config['username'], 'password': config['password']}
)
```

## ข้อกำหนด
- Python 3.x
- python-gnupg library (สำหรับ GPG functions)
- GPG/GnuPG software ติดตั้งบนระบบ
- requests library (สำหรับ API testing)

## ความปลอดภัย
- เก็บไฟล์ Auth.json ให้ปลอดภัย
- ใช้ strong passwords สำหรับ GPG keys
- ห้าม commit sensitive data ลง version control
- ใช้ .gitignore สำหรับไฟล์ที่มี credentials

## หมายเหตุ
- ไฟล์เหล่านี้เป็น development tools
- ควรใช้งานในสภาพแวดล้อมที่ปลอดภัย
- ตรวจสอบการทำงานของ GPG บนระบบก่อนใช้งาน