# AutomateDEV

## ภาพรวม
โปรเจค AutomateDEV เป็นชุดเครื่องมือและแอปพลิเคชันสำหรับการทำงานอัตโนมัติในหลากหลายแพลตฟอร์มและบริการ รวมถึงการจัดการข้อมูล การพัฒนา API และการเชื่อมต่อกับบริการต่างๆ

## โครงสร้างโปรเจค

### 📁 AWS/
- **csv_to_parquet.py**: สคริปต์สำหรับแปลงไฟล์ CSV เป็นรูปแบบ Parquet โดยใช้ Apache Spark และ AWS Glue
- **emr_job.py**: งานสำหรับ Amazon EMR (Elastic MapReduce)

### 📁 Azure/
- **API/Demo/**: โปรเจค Azure Functions สำหรับสร้าง API และ Microsoft Teams Copilot Plugin

### 📁 Copilot/
- **SendMessage/**: ตัวอย่างการเชื่อมต่อและส่งข้อความไปยัง Microsoft Copilot
  - `sendMessageOneTimes.py`: ส่งข้อความครั้งเดียว
  - `sendMessageSequnce.py`: ส่งข้อความต่อเนื่อง
  - `sendMessageUT.py`: Unit test สำหรับการส่งข้อความ

### 📁 ETC/
- **GenerateIcon/**: เครื่องมือสำหรับสร้างไอคอน

### 📁 Gemini/
- **SendMessage/**: การเชื่อมต่อกับ Google Gemini AI
  - `sendMessage.py`: ส่งข้อความไปยัง Gemini AI API

### 📁 generatePython/
- **generateDictionary.py**: เครื่องมือสำหรับสร้างและจัดการ Python dictionary อัตโนมัติ
- **source/**: โฟลเดอร์ source code
- **Target/**: โฟลเดอร์ผลลัพธ์

### 📁 Google/
- **DCA.gs**: Google Apps Script สำหรับ DCA (Digital Certificate Authority)
- **ImNoti.gs**: Google Apps Script สำหรับการแจ้งเตือนภาพ

### 📁 LogicGate/
- **app.py**: แอปพลิเคชันหลัก (ว่าง)
- **processLogicGate.py**: เครื่องมือสำหรับประมวลผล Logic Gate และ Boolean Expression

### 📁 Stonebranch/
เครื่องมือครบครบชุดสำหรับการจัดการ Stonebranch Universal Automation Center (UAC)
- **App/**: GUI Application หหลัก
- **API/**: เครื่องมือสำหรับเรียกใช้ Stonebranch API
- **CLI/**: เครื่องมือ Command Line Interface
- **Excel/**: เครื่องมือสำหรับจัดการ Excel files
- **JIL/**: เครื่องมือสำหรับจัดการ JIL (Job Information Language)
- **utils/**: Utility functions และ helper modules

### 📁 TEST/
- **test.py**: ไฟล์ทดสอบทั่วไป
- **gpg.py**, **gpg_gen.py**: เครื่องมือสำหรับการเข้ารหัส GPG

### 📁 Web/
- **askme_web.html**: หน้าเว็บสำหรับระบบถาม-ตอบ
- **itdesk_index.html**: หน้าเว็บหลักสำหรับ IT Help Desk
- **style.css**: ไฟล์ CSS สำหรับตกแต่งหน้าเว็บ

## ไฟล์หลัก
- **Auth.json**: ไฟล์การตั้งค่าการยืนยันตัวตน
- **Domain.json**: การตั้งค่า Domain
- **STB_Map_Excel.json**: การแมป Excel สำหรับ Stonebranch
- **compare_path.xlsm**: Excel macro สำหรับเปรียบเทียบ path

## การติดตั้งและใช้งาน
โปรดดูรายละเอียดในแต่ละโฟลเดอร์ย่อยสำหรับขั้นตอนการติดตั้งและใช้งานเฉพาะ

## ข้อกำหนด
- Python 3.x
- Node.js (สำหรับโปรเจค Azure)
- Various Python packages (ตามที่ระบุในแต่ละโปรเจค)