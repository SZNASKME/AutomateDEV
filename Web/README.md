# Web Interface

## ภาพรวม
ส่วนติดต่อผู้ใช้แบบเว็บสำหรับระบบต่างๆ รวมถึง Help Desk และระบบถาม-ตอบ

## ไฟล์

### askme_web.html
**วัตถุประสงค์**: หน้าเว็บสำหรับระบบถาม-ตอบ (Q&A System)

**คุณสมบัติ**:
- Interface สำหรับการถามคำถาม
- การแสดงคำตอบและ knowledge base
- ระบบค้นหาคำถามที่เคยถาม
- การจัดหมวดหมู่คำถาม-คำตอบ

**การใช้งาน**:
- เปิดในเว็บเบราว์เซอร์
- ใช้สำหรับ internal knowledge sharing
- รองรับการค้นหาและ filter

### itdesk_index.html
**วัตถุประสงค์**: หน้าเว็บหลักสำหรับ IT Help Desk System

**คุณสมบัติ**:
- Dashboard สำหรับ IT support team
- การจัดการ tickets และ requests
- การติดตามสถานะการแก้ไขปัญหา
- ระบบการรายงานและสถิติ
- ส่วนติดต่อผู้ใช้สำหรับแจ้งปัญหา

**การใช้งาน**:
- หน้าหลักของระบบ IT Help Desk
- จัดการ service requests
- ติดตามการแก้ไขปัญหา

### style.css
**วัตถุประสงค์**: ไฟล์ CSS สำหรับตกแต่งหน้าเว็บทั้งหมด

**คุณสมบัติ**:
- Responsive design
- การออกแบบที่สอดคล้องกัน
- Theme และ color scheme
- Typography และ layout
- Mobile-friendly interface

## โครงสร้างหน้าเว็บ

### IT Help Desk (itdesk_index.html)
```html
<!-- ตัวอย่างโครงสร้าง -->
<header>
  <nav><!-- เมนูหลัก --></nav>
</header>

<main>
  <section class="dashboard">
    <!-- แดชบอร์ดสำหรับแสดงสถิติ -->
  </section>
  
  <section class="ticket-management">
    <!-- การจัดการ tickets -->
  </section>
  
  <section class="knowledge-base">
    <!-- ฐานความรู้ -->
  </section>
</main>
```

### Ask Me System (askme_web.html)
```html
<!-- ตัวอย่างโครงสร้าง -->
<div class="search-container">
  <!-- ช่องค้นหาคำถาม -->
</div>

<div class="question-form">
  <!-- ฟอร์มสำหรับถามคำถามใหม่ -->
</div>

<div class="qa-results">
  <!-- แสดงผลคำถาม-คำตอบ -->
</div>
```

## การติดตั้งและใช้งาน

### 1. การติดตั้ง Web Server
```bash
# สำหรับ development - ใช้ Python HTTP Server
python -m http.server 8000

# หรือใช้ Node.js
npx http-server

# สำหรับ production - ใช้ Apache/Nginx
```

### 2. การเปิดหน้าเว็บ
```
# IT Help Desk
http://localhost:8000/itdesk_index.html

# Ask Me System  
http://localhost:8000/askme_web.html
```

### 3. การปรับแต่ง CSS
```css
/* แก้ไขใน style.css */
:root {
  --primary-color: #007bff;
  --secondary-color: #6c757d;
  --background-color: #f8f9fa;
}

/* Responsive breakpoints */
@media (max-width: 768px) {
  /* Mobile styles */
}
```

## ฟีเจอร์หลัก

### IT Help Desk Features
- **Ticket Management**: สร้าง, แก้ไข, ปิด tickets
- **Priority System**: จัดลำดับความสำคัญ
- **Status Tracking**: ติดตามสถานะการแก้ไข
- **Reporting**: รายงานและสถิติ
- **Knowledge Base**: ฐานความรู้สำหรับ self-service

### Ask Me System Features
- **Question Submission**: ส่งคำถามใหม่
- **Search Functionality**: ค้นหาคำถามที่เคยถาม
- **Category Filtering**: กรองตามหมวดหมู่
- **Vote System**: โหวตความเป็นประโยชน์ของคำตอบ
- **Expert Answers**: คำตอบจากผู้เชี่ยวชาญ

## การเชื่อมต่อ Backend

### JavaScript Integration
```javascript
// ตัวอย่างการเรียก API
async function submitTicket(ticketData) {
  try {
    const response = await fetch('/api/tickets', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(ticketData)
    });
    
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Error:', error);
  }
}

// การโหลดข้อมูล
async function loadTickets() {
  const tickets = await fetch('/api/tickets');
  const data = await tickets.json();
  displayTickets(data);
}
```

## การปรับแต่ง

### 1. การเปลี่ยน Theme
```css
/* Dark theme */
body.dark-theme {
  background-color: #1a1a1a;
  color: #ffffff;
}

/* Corporate theme */
body.corporate-theme {
  --primary-color: #2c3e50;
  --accent-color: #3498db;
}
```

### 2. การเพิ่มฟีเจอร์ใหม่
```html
<!-- เพิ่มส่วนใหม่ใน HTML -->
<section class="new-feature">
  <h2>ฟีเจอร์ใหม่</h2>
  <!-- เนื้อหาของฟีเจอร์ -->
</section>
```

## ข้อกำหนด
- เว็บเบราว์เซอร์ที่รองรับ HTML5, CSS3, JavaScript ES6+
- Web Server (Apache, Nginx, IIS หรือ development server)
- Backend API (ถ้าต้องการ dynamic content)

## Browser Support
- Chrome 70+
- Firefox 65+
- Safari 12+
- Edge 79+

## หมายเหตุ
- ไฟล์เหล่านี้เป็น frontend เท่านั้น
- ต้องการ backend API สำหรับการทำงานแบบ dynamic
- ควรใช้ HTTPS สำหรับ production
- ทดสอบใน browsers หลายตัวก่อน deploy