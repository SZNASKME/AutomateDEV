# Logic Gate Processor

## ภาพรวม
เครื่องมือสำหรับประมวลผล Logic Gate และ Boolean Expression โดยใช้ SymPy library

## ไฟล์

### app.py
**วัตถุประสงค์**: แอปพลิเคชันหลัก (ปัจจุบันยังว่าง - พร้อมสำหรับพัฒนาต่อ)

**การใช้งาน**: 
- เตรียมไว้สำหรับสร้าง GUI หรือ web interface
- สามารถพัฒนาเป็น Flask/Django web app
- หรือ desktop application ด้วย tkinter/PyQt

### processLogicGate.py
**วัตถุประสงค์**: เครื่องมือหลักสำหรับประมวลผล Boolean logic และ Logic Gate

**ฟีเจอร์หลัก**:

#### 1. การทำให้ Boolean Expression เรียบง่าย
```python
def simplify_logic_expression(expression: str) -> str
```
- **วัตถุประสงค์**: ทำให้ Boolean expression เรียบง่ายขึ้น
- **พารามิเตอร์**: `expression` - สตริงของ Boolean expression
- **คืนค่า**: สตริงของ simplified expression
- **รองรับตัวแปร**: A-Z (26 ตัวแปร)

#### 2. การแปลงเป็น Logic Gate
```python
def logic_gate(expression: str) -> str
```
- **วัตถุประสงค์**: แปลง Boolean expression เป็นรูปแบบ Logic Gate
- **พารามิเตอร์**: `expression` - สตริงของ Boolean expression  
- **คืนค่า**: สตริงในรูปแบบ Logic Gate notation
- **รองรับ Gates**: AND, OR, NOT, XOR

## ตัวอย่างการใช้งาน

### 1. การทำให้ Expression เรียบง่าย
```python
# ตัวอย่างพื้นฐาน
expression = "(A & B) | (~A & B)"
simplified = simplify_logic_expression(expression)
print(simplified)  # ผลลัพธ์: B

# ตัวอย่างซับซ้อนกว่า
complex_expr = "(A & B & C) | (A & B & ~C) | (~A & B & C)"
simplified = simplify_logic_expression(complex_expr)
print(simplified)  # ผลลัพธ์ที่ทำให้เรียบง่าย
```

### 2. การแปลงเป็น Logic Gate
```python
expression = "(A & B) | (~A & B)"
gates = logic_gate(expression)
print(gates)  # ผลลัพธ์: OR(AND(A, B), AND(NOT(A), B))

# ตัวอย่าง XOR
xor_expr = "A ^ B"
gates = logic_gate(xor_expr)
print(gates)  # ผลลัพธ์: XOR(A, B)
```

### 3. การใช้งานครบวงจร
```python
from processLogicGate import simplify_logic_expression, logic_gate

# Input expression
original = "(A & B & C) | (A & ~B & C) | (~A & B & C)"

# Step 1: Simplify
simplified = simplify_logic_expression(original)
print(f"Original: {original}")
print(f"Simplified: {simplified}")

# Step 2: Convert to logic gates
gates = logic_gate(simplified)
print(f"Logic Gates: {gates}")
```

## รูปแบบ Boolean Expression ที่รองรับ

### Operators
- `&` หรือ `*`: AND operation
- `|` หรือ `+`: OR operation  
- `~` หรือ `!`: NOT operation
- `^`: XOR operation

### Variables
- รองรับตัวแปร A-Z (ทั้งหมด 26 ตัว)
- Case-sensitive

### ตัวอย่าง Expression
```python
# AND Gate
"A & B"
"A * B"

# OR Gate  
"A | B"
"A + B"

# NOT Gate
"~A"
"!A"

# XOR Gate
"A ^ B"

# Complex Expression
"(A & B) | (~C & D)"
"(A | B) & (~C | D)"
```

## ข้อกำหนด
- Python 3.x
- SymPy library

### การติดตั้ง SymPy
```bash
pip install sympy
```

## Use Cases
- การออกแบบวงจรดิจิทัล
- การวิเคราะห์ Boolean algebra
- การเรียนการสอนเรื่อง Logic Gate
- การทำให้ Boolean expression เรียบง่าย
- การแปลงสมการ Boolean เป็น Hardware description

## การพัฒนาต่อ
```python
# สามารถเพิ่มฟังก์ชันใหม่ได้ เช่น
def generate_truth_table(expression: str) -> dict:
    """สร้าง Truth Table จาก Boolean expression"""
    pass

def draw_logic_circuit(expression: str) -> None:
    """วาดแผนภาพวงจรลอจิก"""
    pass
```