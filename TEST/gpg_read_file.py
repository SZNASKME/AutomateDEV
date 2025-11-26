

# 1. อ่านเนื้อหาของไฟล์ Key เข้ามาเป็นสตริง
with open('my_public_key.asc', 'rb') as f:
    key_data = f.read()