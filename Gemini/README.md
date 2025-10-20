# Google Gemini AI Integration

## ภาพรวม
เครื่องมือสำหรับการเชื่อมต่อและส่งข้อความไปยัง Google Gemini AI โดยใช้ Google Generative AI SDK

## โครงสร้าง

### 📁 configs/
ไฟล์การตั้งค่าสำหรับ Gemini AI (ถ้ามี)

### 📁 SendMessage/

#### sendMessage.py
**วัตถุประสงค์**: ส่งข้อความไปยัง Google Gemini AI และรับคำตอบ

**ฟีเจอร์หลัก**:
- การเชื่อมต่อ Gemini AI แบบ asynchronous
- รองรับ Gemini 1.5 Flash model
- การจัดการ API key และ project configuration
- Error handling สำหรับการเชื่อมต่อ

**การตั้งค่า**:
```python
INPUT_TEXT = "What is SLA?"  # ข้อความที่ต้องการส่ง
API_KEY = ""  # ใส่ Google AI API key ของคุณ
PROJECT_NAME = "275082005270"  # Project ID
MODEL = "gemini-1.5-flash"  # รุ่นของ model ที่จะใช้
```

**ฟังก์ชันหลัก**:
- `getMessages(model)`: ส่งข้อความและรับคำตอบแบบ async
- `main()`: ฟังก์ชันหลักสำหรับรันโปรแกรม

#### sendMessageUT.py
**วัตถุประสงค์**: Unit tests สำหรับการทดสอบฟังก์ชันการส่งข้อความไปยัง Gemini

**การทดสอบ**:
- ทดสอบการเชื่อมต่อ API
- ทดสอบการส่งและรับข้อความ
- ทดสอบ error handling
- ทดสอบ async operations

## วิธีใช้งาน

### 1. การติดตั้ง dependencies
```bash
pip install google-generativeai
```

### 2. การตั้งค่า API Key
1. ไปที่ [Google AI Studio](https://makersuite.google.com/app/apikey)
2. สร้าง API key ใหม่
3. แก้ไขค่า `API_KEY` ใน sendMessage.py

### 3. การรันโปรแกรม
```bash
python sendMessage.py
```

### 4. การรัน Unit Tests
```bash
python sendMessageUT.py
```

## ตัวอย่างการใช้งาน
```python
import asyncio
import google.generativeai as genai

async def example():
    genai.configure(api_key="YOUR_API_KEY")
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    response = await model.generate_content_async("อธิบายเกี่ยวกับ AI")
    print(response.text)

# รันโปรแกรม
asyncio.run(example())
```

## ข้อกำหนด
- Python 3.7+
- google-generativeai package
- Valid Google AI API key
- Internet connection

## หมายเหตุ
- ต้องมี Google AI API key ที่ valid
- รองรับการทำงานแบบ asynchronous
- สามารถเปลี่ยน model ได้ตามต้องการ (gemini-pro, gemini-1.5-flash, etc.)