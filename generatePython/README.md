# Python Dictionary Generator

## ภาพรวม
เครื่องมือสำหรับสร้างและจัดการ Python dictionary อัตโนมัติ โดยสามารถวิเคราะห์และประมวลผล dictionary จากหลายไฟล์

## ไฟล์หลัก

### generateDictionary.py
**วัตถุประสงค์**: เครื่องมือหลักสำหรับการสร้างและประมวลผล Python dictionary

**ฟีเจอร์หลัก**:
- โหลด dictionary จากไฟล์ Python
- วิเคราะห์ชื่อ dictionary variables ในไฟล์
- หาค่า intersection ระหว่าง dictionary หลายตัว
- สร้างไฟล์ผลลัพธ์อัตโนมัติ

**ฟังก์ชันสำคัญ**:

#### `load_dict_from_file(file_path, dict_name)`
- โหลด dictionary จากไฟล์ Python module
- **พารามิเตอร์**:
  - `file_path`: path ของไฟล์ Python
  - `dict_name`: ชื่อของ dictionary variable
- **คืนค่า**: dictionary object

#### `get_dict_names_from_file(file_path)`
- วิเคราะห์และดึงชื่อ dictionary variables จากไฟล์
- **พารามิเตอร์**: `file_path` - path ของไฟล์ Python
- **คืนค่า**: list ของชื่อ dictionary variables

#### `find_intersection(dict_data)`
- หาค่าที่ซ้ำกันระหว่าง dictionary หลายตัว
- **พารามิเตอร์**: `dict_data` - dictionary ของ dictionaries
- **คืนค่า**: dictionary ที่มีค่าร่วมกัน

**การตั้งค่า**:
```python
TARGET_FILE_PATH = ".\\Target\\mappingField.py"  # ไฟล์ผลลัพธ์
SOURCE_FILE_PATH = ".\\source\\mappingField.py"  # ไฟล์ต้นฉบับ
```

## โครงสร้าง

### 📁 source/
เก็บไฟล์ต้นฉบับที่มี dictionary definitions

#### mappingField.py
**วัตถุประสงค์**: ไฟล์ที่เก็บ field mapping dictionaries

**รูปแบบ**:
```python
# ตัวอย่างโครงสร้าง dictionary
mapping_dict_1 = {
    "field1": "value1",
    "field2": "value2",
    "common_field": "common_value"
}

mapping_dict_2 = {
    "field3": "value3", 
    "field4": "value4",
    "common_field": "common_value"
}
```

### 📁 Target/
เก็บไฟล์ผลลัพธ์ที่สร้างจากการประมวลผล

## วิธีใช้งาน

### 1. การเตรียมไฟล์ต้นฉบับ
```python
# สร้างไฟล์ source/mappingField.py
source_dict = {
    "name": "John",
    "age": 30,
    "city": "Bangkok"
}

target_dict = {
    "name": "Jane", 
    "age": 25,
    "country": "Thailand"
}
```

### 2. การรันโปรแกรม
```python
python generateDictionary.py
```

### 3. ตัวอย่างการใช้ฟังก์ชัน
```python
# โหลด dictionary จากไฟล์
source_data = load_dict_from_file("source/mappingField.py", "source_dict")

# หาชื่อ dictionary ทั้งหมดในไฟล์
dict_names = get_dict_names_from_file("source/mappingField.py")
print(dict_names)  # ['source_dict', 'target_dict']

# หาค่าที่ซ้ำกัน
dict_collection = {
    "dict1": {"a": 1, "b": 2, "c": 3},
    "dict2": {"b": 2, "c": 3, "d": 4}
}
intersection = find_intersection(dict_collection)
print(intersection)  # {'b': 2, 'c': 3}
```

## ข้อกำหนด
- Python 3.x
- Standard libraries: os, importlib, ast, json

## Use Cases
- การรวม field mapping จากหลายแหล่ง
- การหาค่าที่ซ้ำกันระหว่าง configuration files
- การสร้าง unified dictionary จาก multiple sources
- การวิเคราะห์โครงสร้างข้อมูลใน Python modules