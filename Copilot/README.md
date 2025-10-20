# Microsoft Copilot Integration

## ภาพรวม
เครื่องมือสำหรับการเชื่อมต่อและส่งข้อความไปยัง Microsoft Copilot โดยใช้ Direct Line API

## โครงสร้าง

### 📁 configs/
- **sendMessage.json**: ไฟล์การตั้งค่าสำหรับการส่งข้อความ

### 📁 SendMessage/
เก็บสคริปต์ต่างๆ สำหรับการส่งข้อความไปยัง Copilot

#### sendMessageOneTimes.py
**วัตถุประสงค์**: ส่งข้อความครั้งเดียวไปยัง Microsoft Copilot

**ฟีเจอร์หลัก**:
- การขอ token สำหรับ Direct Line API
- สร้าง conversation session
- ส่งข้อความและรับคำตอบ
- รองรับ retry mechanism
- รองรับ Thai locale (th-TH)

**การตั้งค่า**:
```python
ops_copilot_token_url = "https://..."  # URL สำหรับขอ token
ops_copilot_input_text = "What is stonebranch?"  # ข้อความที่ต้องการส่ง
ops_copilot_maximum_retry = 3  # จำนวนครั้งที่จะ retry
ops_copilot_retry_interval = 10  # ระยะเวลารอระหว่าง retry (วินาที)
```

#### sendMessageSequence.py
**วัตถุประสงค์**: ส่งข้อความต่อเนื่องหลายครั้งในการสนทนาเดียวกัน

**คุณสมบัติ**:
- รักษา conversation context
- ส่งข้อความหลายข้อความในลำดับ
- จัดการ session timeout

#### sendMessageUT.py
**วัตถุประสงค์**: Unit tests สำหรับการทดสอบฟังก์ชันการส่งข้อความ

**การทดสอบ**:
- ทดสอบการขอ token
- ทดสอบการสร้าง conversation
- ทดสอบการส่งและรับข้อความ
- ทดสอบ error handling

## วิธีใช้งาน

### 1. การตั้งค่าเริ่มต้น
```python
# แก้ไข URL และ token ใน sendMessageOneTimes.py
ops_copilot_token_url = "YOUR_COPILOT_TOKEN_URL"
```

### 2. การส่งข้อความครั้งเดียว
```python
python sendMessageOneTimes.py
```

### 3. การส่งข้อความต่อเนื่อง
```python
python sendMessageSequence.py
```

### 4. การรัน Unit Tests
```python
python sendMessageUT.py
```

## ข้อกำหนด
- Python 3.x
- requests library
- Microsoft Copilot Direct Line API access
- Valid authentication token

## หมายเหตุ
- ต้องมี valid Direct Line API endpoint
- ต้องตั้งค่า authentication ให้ถูกต้อง
- รองรับ locale th-TH สำหรับภาษาไทย