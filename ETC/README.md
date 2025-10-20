# Miscellaneous Tools and Utilities

## ภาพรวม
เครื่องมือเบ็ดเตล็ดและ utilities ต่างๆ รวมถึงการสร้างไอคอน

## โครงสร้าง

### 📁 GenerateIcon/
เครื่องมือสำหรับสร้างไอคอนแบบอัตโนมัติ

#### genIcon.py
**วัตถุประสงค์**: สร้างไอคอนในรูปแบบต่างๆ สำหรับแอปพลิเคชัน

**คุณสมบัติ**:
- สร้างไอคอนหลายขนาด (16x16, 32x32, 64x64, 128x128, 256x256)
- รองรับหลายรูปแบบ (.ico, .png, .jpg, .svg)
- การ resize อัตโนมัติ
- การปรับคุณภาพภาพ
- การสร้าง favicon สำหรับเว็บไซต์

**ฟังก์ชันหลัก**:
```python
def generate_icon(source_image, output_sizes, output_format):
    """
    สร้างไอคอนจากภาพต้นฉบับ
    
    Args:
        source_image: path ของภาพต้นฉบับ
        output_sizes: list ของขนาดที่ต้องการ [16, 32, 64, 128, 256]
        output_format: รูปแบบผลลัพธ์ ('ico', 'png', 'jpg')
    """
    pass

def create_favicon(source_image, output_path):
    """สร้าง favicon.ico สำหรับเว็บไซต์"""
    pass

def batch_generate_icons(source_folder, output_folder):
    """สร้างไอคอนจากภาพหลายไฟล์พร้อมกัน"""
    pass
```

## วิธีใช้งาน

### 1. การติดตั้ง Dependencies
```bash
pip install Pillow  # สำหรับการจัดการภาพ
pip install cairosvg  # สำหรับ SVG support (optional)
```

### 2. การสร้างไอคอนพื้นฐาน
```python
from genIcon import generate_icon

# สร้างไอคอนจากภาพต้นฉบับ
source = "logo.png"
sizes = [16, 32, 48, 64, 128, 256]
generate_icon(source, sizes, "ico")
```

### 3. การสร้าง Favicon
```python
from genIcon import create_favicon

# สร้าง favicon สำหรับเว็บไซต์
create_favicon("logo.png", "favicon.ico")
```

### 4. การประมวลผลแบบ Batch
```python
from genIcon import batch_generate_icons

# สร้างไอคอนจากภาพทั้งหมดในโฟลเดอร์
batch_generate_icons("source_images/", "output_icons/")
```

## ตัวอย่างการใช้งาน

### 1. สร้างไอคอนสำหรับแอปพลิเคชัน Desktop
```python
import os
from genIcon import generate_icon

def create_app_icons(app_name, source_image):
    """สร้างไอคอนสำหรับแอปพลิเคชัน"""
    
    # ขนาดมาตรฐานสำหรับแอป Desktop
    desktop_sizes = [16, 32, 48, 64, 128, 256]
    
    # สร้างโฟลเดอร์สำหรับเก็บไอคอน
    icon_folder = f"icons/{app_name}"
    os.makedirs(icon_folder, exist_ok=True)
    
    # สร้างไอคอน .ico
    generate_icon(source_image, desktop_sizes, "ico")
    
    # สร้างไอคอน .png สำหรับแต่ละขนาด
    for size in desktop_sizes:
        generate_icon(source_image, [size], "png")
```

### 2. สร้างไอคอนสำหรับ Web Application
```python
def create_web_icons(source_image, output_folder):
    """สร้างไอคอนสำหรับเว็บแอป"""
    
    # ขนาดมาตรฐานสำหรับเว็บ
    web_sizes = [16, 32, 180, 192, 512]
    
    # สร้าง favicon
    create_favicon(source_image, f"{output_folder}/favicon.ico")
    
    # สร้าง Apple touch icons
    generate_icon(source_image, [180], "png", f"{output_folder}/apple-touch-icon.png")
    
    # สร้าง PWA icons
    for size in [192, 512]:
        output_name = f"{output_folder}/icon-{size}x{size}.png"
        generate_icon(source_image, [size], "png", output_name)
```

### 3. การปรับแต่งคุณภาพและ Optimization
```python
def generate_optimized_icon(source_image, sizes, quality=95):
    """สร้างไอคอนที่ปรับแต่งคุณภาพแล้ว"""
    
    from PIL import Image, ImageFilter
    
    # โหลดภาพต้นฉบับ
    img = Image.open(source_image)
    
    # ปรับปรุงคุณภาพภาพ
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # เพิ่ม anti-aliasing
    img = img.resize((max(sizes) * 2, max(sizes) * 2), Image.LANCZOS)
    
    for size in sizes:
        # Resize แบบ high quality
        resized = img.resize((size, size), Image.LANCZOS)
        
        # เพิ่ม sharpening เล็กน้อย
        resized = resized.filter(ImageFilter.SHARPEN)
        
        # บันทึกไฟล์
        output_path = f"icon_{size}x{size}.png"
        resized.save(output_path, "PNG", quality=quality, optimize=True)
```

## การตั้งค่าขั้นสูง

### 1. การสร้างไอคอนแบบ Gradient
```python
def create_gradient_icon(size, start_color, end_color, shape="circle"):
    """สร้างไอคอนแบบ gradient"""
    
    from PIL import Image, ImageDraw
    
    # สร้างภาพใหม่
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # สร้าง gradient effect
    for i in range(size):
        ratio = i / size
        color = interpolate_color(start_color, end_color, ratio)
        
        if shape == "circle":
            draw.ellipse([i//4, i//4, size-i//4, size-i//4], fill=color)
        else:
            draw.rectangle([i//4, i//4, size-i//4, size-i//4], fill=color)
    
    return img
```

### 2. การเพิ่ม Text บนไอคอน
```python
def add_text_to_icon(image, text, font_size=None):
    """เพิ่มข้อความบนไอคอน"""
    
    from PIL import ImageDraw, ImageFont
    
    draw = ImageDraw.Draw(image)
    
    # ปรับขนาดฟอนต์อัตโนมัติ
    if font_size is None:
        font_size = image.size[0] // 4
    
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # คำนวณตำแหน่งข้อความ
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = (image.size[0] - text_width) // 2
    y = (image.size[1] - text_height) // 2
    
    # วาดข้อความ
    draw.text((x, y), text, fill="white", font=font)
    
    return image
```

## ข้อกำหนด
- Python 3.x
- Pillow (PIL) library
- cairosvg (สำหรับ SVG support - optional)

## Use Cases
- สร้างไอคอนสำหรับ desktop applications
- สร้าง favicon สำหรับเว็บไซต์
- สร้างไอคอนสำหรับ mobile apps
- การ batch processing ไอคอนหลายขนาด
- การสร้างไอคอนจาก brand guidelines

## หมายเหตุ
- รองรับรูปแบบภาพ: PNG, JPG, BMP, GIF, TIFF
- ผลลัพธ์ที่ดีที่สุดได้จากภาพต้นฉบับความละเอียดสูง
- ควรใช้ภาพ square aspect ratio (1:1) สำหรับไอคอน
- ตรวจสอบ copyright ของภาพต้นฉบับก่อนใช้งาน