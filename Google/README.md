# Google Apps Script Tools

## ภาพรวม
เครื่องมือ Google Apps Script สำหรับงานต่างๆ ที่เกี่ยวข้องกับ Google Workspace

## ไฟล์

### DCA.gs
**วัตถุประสงค์**: Google Apps Script สำหรับ DCA (Digital Certificate Authority) functions

**คุณสมบัติ**:
- การจัดการ digital certificates
- การตรวจสอบและยืนยันใบรับรอง
- การเชื่อมต่อกับ certificate authority services
- การจัดการ certificate lifecycle

**การใช้งาน**:
- ใช้ใน Google Sheets หรือ Google Apps environment
- สำหรับการจัดการใบรับรองดิจิทัล
- การ validate certificate status

### ImNoti.gs  
**วัตถุประสงค์**: Google Apps Script สำหรับการแจ้งเตือนเกี่ยวกับรูปภาพ (Image Notification)

**คุณสมบัติ**:
- การส่งการแจ้งเตือนเมื่อมีการอัพโหลดรูปภาพใหม่
- การประมวลผลรูปภาพและส่งแจ้งเตือน
- การเชื่อมต่อกับ Google Drive หรือ Google Photos
- การส่ง notification ผ่าน Gmail หรือ Google Chat

**การใช้งาน**:
- ติดตั้งใน Google Apps Script project
- เชื่อมต่อกับ Google Drive triggers
- ตั้งค่าการแจ้งเตือนอัตโนมัติ

## การติดตั้งและใช้งาน

### 1. การติดตั้งใน Google Apps Script
1. เปิด [Google Apps Script](https://script.google.com/)
2. สร้างโปรเจคใหม่
3. คัดลอกโค้ดจากไฟล์ .gs ไปยัง Script Editor
4. บันทึกและตั้งชื่อโปรเจค

### 2. การตั้งค่า Permissions
```javascript
// ตัวอย่างการขออนุญาตใช้งาน Google Services
function onOpen() {
  // ขออนุญาตใช้งาน Google Drive
  DriveApp.getFiles();
  
  // ขออนุญาตใช้งาน Gmail
  GmailApp.getInboxThreads(0, 1);
}
```

### 3. การตั้งค่า Triggers
```javascript
// ตั้งค่า trigger สำหรับเหตุการณ์ต่างๆ
function createTriggers() {
  // Trigger เมื่อมีไฟล์ใหม่ใน Google Drive
  ScriptApp.newTrigger('onFileChange')
           .create();
}
```

## ตัวอย่างการใช้งาน

### DCA.gs - Certificate Management
```javascript
// ตัวอย่างการตรวจสอบ certificate
function checkCertificateStatus(certificateId) {
  // Logic สำหรับตรวจสอบสถานะใบรับรอง
  var status = getCertificateFromAuthority(certificateId);
  return status;
}
```

### ImNoti.gs - Image Notification
```javascript  
// ตัวอย่างการส่งการแจ้งเตือนเมื่อมีรูปภาพใหม่
function onNewImage(file) {
  if (isImageFile(file)) {
    sendNotification(file.getName(), file.getUrl());
  }
}
```

## ข้อกำหนด
- Google Account
- Google Apps Script access
- ตั้งค่า OAuth permissions สำหรับ Google Services ที่จำเป็น

## การตั้งค่าความปลอดภัย
- ตรวจสอบ sharing permissions
- ตั้งค่า execution permissions อย่างเหมาะสม  
- ใช้ PropertiesService สำหรับเก็บค่า sensitive data

## หมายเหตุ
- ไฟล์ .gs เป็นส่วนขยายของ Google Apps Script
- ต้องการการอนุญาตจาก Google สำหรับการเข้าถึงข้อมูล
- ควรทดสอบการทำงานในโหมด development ก่อนใช้งานจริง