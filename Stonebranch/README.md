# Stonebranch Universal Automation Center (UAC) Toolkit Extended

## ภาพรวม
ชุดเครื่องมือครบครบสำหรับการจัดการ Stonebranch Universal Automation Center (UAC) รวมถึง GUI Application, API tools, Excel utilities และอื่นๆ

## โครงสร้างหลัก

### 📁 App/ - GUI Application
**วัตถุประสงค์**: แอปพลิเคชัน Desktop ด้วย GUI สำหรับจัดการ Stonebranch UAC

**ไฟล์หลัก**:
- **main.py**: จุดเริ่มต้นของแอปพลิเคชัน
- **GUI.py**: User Interface หลักที่ใช้ CustomTkinter
- **requirements.txt**: รายการ Python packages ที่จำเป็น

**คุณสมบัติ**:
- GUI ที่ใช้งานง่ายด้วย CustomTkinter
- ระบบจัดการ features แบบ dynamic
- Console logging แบบ real-time
- การจัดการ configuration files
- รองรับการทำงานแบบ multi-threading

### 📁 API/ - API Integration Tools
**วัตถุประสงค์**: เครื่องมือสำหรับเรียกใช้ Stonebranch UAC REST API

**โฟลเดอร์ย่อย**:
- **Action/**: การจัดการ Actions และ Check Actions
- **Audit/**: การดึงข้อมูล Audit logs
- **Bundle/**: การจัดการ Bundles และ Bundle reports
- **Children/**: การหา Child tasks และ dependencies
- **Task/**: การจัดการ Tasks ต่างๆ
- **TaskMonitor/**: การ monitor สถานะของ Tasks
- **Trigger/**: การจัดการ Triggers
- **Workflow/**: การจัดการ Workflows
- **UAC/**: การจัดการ UAC configurations

### 📁 CLI/ - Command Line Interface
**วัตถุประสงค์**: เครื่องมือ Command Line สำหรับการทำงานแบบ batch หรือ automation

### 📁 CrossPlatform/ - Cross Platform Tools
**วัตถุประสงค์**: เครื่องมือเปรียบเทียบและจัดการข้อมูลข้าม platforms

**โฟลเดอร์ย่อย**:
- **CompareTaskAndCondition/**: เปรียบเทียบ Tasks และ Conditions
- **CompareDependencies/**: เปรียบเทียบ Dependencies
- **CompareFormat/**: เปรียบเทียบรูปแบบข้อมูล
- **CompareTask/**: เปรียบเทียบ Tasks
- **GetReportCompareExcel/**: สร้างรายงานเปรียบเทียบใน Excel
- **ReArrange/**: จัดเรียงข้อมูลใหม่

### 📁 Excel/ - Excel Utilities
**วัตถุประสงค์**: เครื่องมือสำหรับจัดการไฟล์ Excel

**ไฟล์หลัก**:
- **json_to_excel.py**: แปลงไฟล์ JSON เป็น Excel format

**คุณสมบัติ**:
```python
# ตัวอย่างการใช้งาน json_to_excel.py
def convert_json_to_excel():
    - อ่านไฟล์ TaskInstance01.json
    - แปลงข้อมูล JSON เป็น DataFrame
    - จัดการ customField1, customField2
    - แปลง businessServices จาก list เป็น string
    - จัดเรียงคอลัมน์ใหม่เพื่อให้อ่านง่าย
    - บันทึกเป็นไฟล์ Excel
```

### 📁 Excel_Autosys/ - Autosys Excel Tools
**วัตถุประสงค์**: เครื่องมือสำหรับจัดการ Autosys jobs ผ่าน Excel

### 📁 Excel_BMC/ - BMC Excel Tools  
**วัตถุประสงค์**: เครื่องมือสำหรับ BMC Control-M ที่เกี่ยวข้องกับ Excel

### 📁 JIL/ - Job Information Language Tools
**วัตถุประสงค์**: เครื่องมือสำหรับจัดการ JIL (Job Information Language)

**โฟลเดอร์ย่อย**:
- **ConvertToExcel/**: แปลง JIL เป็น Excel format
- **CreateFromExcel/**: สร้าง JIL จาก Excel  
- **MergeMultiJIL/**: รวม JIL หลายไฟล์เข้าด้วยกัน

### 📁 JSON/ - JSON Processing Tools
**วัตถุประสงค์**: เครื่องมือสำหรับจัดการไฟล์ JSON

### 📁 UniversalTemplate/ - Universal Templates
**วัตถุประสงค์**: Templates สำหรับการเชื่อมต่อกับระบบต่างๆ

**Templates ที่รองรับ**:
- **ApacheAirflow/**: เชื่อมต่อกับ Apache Airflow
- **CS_DataStage/**: IBM DataStage integration  
- **FinishLongTimeTask/**: จัดการ long-running tasks
- **GnuPG/**: การเข้ารหัสด้วย GnuPG
- **JAC/**: Job Access Control
- **Jira/**: เชื่อมต่อกับ Atlassian Jira
- **SSIS/**: SQL Server Integration Services

### 📁 utils/ - Utility Functions
**วัตถุประสงค์**: ฟังก์ชันช่วยเหลือและ utility modules

**ไฟล์หลัก**:
- **stbAPI.py**: Stonebranch API wrapper functions
- **readExcel.py**: อ่านไฟล์ Excel
- **editExcel.py**: แก้ไขไฟล์ Excel
- **readFile.py**: อ่านไฟล์ทั่วไป
- **createFile.py**: สร้างไฟล์
- **convertFormat.py**: แปลงรูปแบบไฟล์

**stbAPI.py Features**:
```python
# ตัวอย่าง API endpoints
TASK_URI = f"{DOMAIN}/task"
TRIGGER_URI = f"{DOMAIN}/trigger" 
BUNDLE_URI = f"{DOMAIN}/bundle"
WORKFLOW_URI = f"{DOMAIN}/workflow"

# Authentication support
auth = HTTPBasicAuth('username', 'password')

# Helper functions
def createURI(uri, configs):
    # สร้าง URI พร้อม parameters
    pass
```

### 📁 WebApp/ - Web Application
**วัตถุประสงค์**: Web-based interface สำหรับ Stonebranch tools

## การติดตั้งและใช้งาน

### 1. Requirements
```bash
# ติดตั้ง Python packages
pip install customtkinter
pip install pandas
pip install requests
pip install tkinter
```

### 2. การรัน GUI Application
```bash
cd Stonebranch/App
python main.py
```

### 3. การใช้งาน API Tools
```python
from utils.stbAPI import *

# ตั้งค่า authentication
auth = HTTPBasicAuth('your_username', 'your_password')

# เรียกใช้ API
response = requests.get(TASK_URI, auth=auth)
```

### 4. การแปลง JSON เป็น Excel
```bash
cd Stonebranch/Excel  
python json_to_excel.py
```

## การตั้งค่า

### 1. การตั้งค่า API Connection
```python
# แก้ไขใน utils/stbAPI.py
DOMAIN = "http://your-uac-server:port/uc/resources"
auth = HTTPBasicAuth('your_username', 'your_password')
```

### 2. การตั้งค่า GUI Application
- แก้ไขไฟล์ config ใน App/config/
- ตั้งค่า features ที่ต้องการใช้งาน
- ปรับแต่ง UI theme และ appearance

## หมายเหตุ
- ต้องมีการเชื่อมต่อกับ Stonebranch UAC server
- ตรวจสอบให้แน่ใจว่า credentials ถูกต้อง
- บาง features อาจต้องการ admin privileges
- รองรับการทำงานบน Windows, macOS และ Linux