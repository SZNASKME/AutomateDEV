import json
import pandas as pd
from datetime import datetime
import os

def convert_json_to_excel():
    """แปลงไฟล์ TaskInstance01.json เป็น Excel"""
    
    # อ่านไฟล์ JSON
    json_file = 'TaskInstance01.json'
    excel_file = 'TaskInstance01.xlsx'
    
    print(f"กำลังอ่านไฟล์ {json_file}...")
    
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        print(f"พบข้อมูล {len(data)} รายการ")
        
        # สร้าง DataFrame
        df = pd.DataFrame(data)
        
        # แยกข้อมูล customField1 และ customField2
        if 'customField1' in df.columns:
            df['customField1_label'] = df['customField1'].apply(lambda x: x.get('label', '') if isinstance(x, dict) else '')
            df['customField1_value'] = df['customField1'].apply(lambda x: x.get('value', '') if isinstance(x, dict) else '')
            df = df.drop('customField1', axis=1)
        
        if 'customField2' in df.columns:
            df['customField2_label'] = df['customField2'].apply(lambda x: x.get('label', '') if isinstance(x, dict) else '')
            df['customField2_value'] = df['customField2'].apply(lambda x: x.get('value', '') if isinstance(x, dict) else '')
            df = df.drop('customField2', axis=1)
        
        # แปลง businessServices จาก list เป็น string
        if 'businessServices' in df.columns:
            df['businessServices'] = df['businessServices'].apply(lambda x: ', '.join(x) if isinstance(x, list) else str(x))
        
        # จัดเรียงคอลัมน์ใหม่เพื่อให้อ่านง่าย
        important_columns = [
            'name', 'taskName', 'status', 'progress', 'agent', 'credentials',
            'launchTime', 'startTime', 'endTime', 'updatedTime',
            'workflowDefinitionName', 'workflowInstanceName',
            'businessServices', 'customField1_label', 'customField1_value',
            'customField2_label', 'customField2_value'
        ]
        
        # เรียงคอลัมน์ที่สำคัญก่อน แล้วตามด้วยคอลัมน์อื่นๆ
        remaining_columns = [col for col in df.columns if col not in important_columns]
        final_columns = [col for col in important_columns if col in df.columns] + remaining_columns
        df = df[final_columns]
        
        # บันทึกเป็น Excel พร้อมจัดรูปแบบ
        print(f"กำลังสร้างไฟล์ Excel...")
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Task_Instances', index=False)
            
            # ปรับความกว้างของคอลัมน์
            worksheet = writer.sheets['Task_Instances']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                # จำกัดความกว้างสูงสุด
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # แช่แข็งแถวหัวตาราง
            worksheet.freeze_panes = 'A2'
        
        print(f"✅ แปลงเสร็จสิ้น!")
        print(f"📊 จำนวนรายการ: {len(df):,} รายการ")
        print(f"📋 จำนวนคอลัมน์: {len(df.columns)} คอลัมน์")
        print(f"📁 ไฟล์ Excel: {excel_file}")
        
        # แสดงข้อมูลสถิติเบื้องต้น
        print("\n📈 สถิติข้อมูล:")
        if 'status' in df.columns:
            print("สถานะ:")
            status_counts = df['status'].value_counts()
            for status, count in status_counts.items():
                print(f"  - {status}: {count:,} รายการ")
        
        if 'agent' in df.columns:
            print(f"\nจำนวน Agent: {df['agent'].nunique()} Agent")
        
        if 'workflowDefinitionName' in df.columns:
            print(f"จำนวน Workflow: {df['workflowDefinitionName'].nunique()} Workflow")
            
    except FileNotFoundError:
        print(f"❌ ไม่พบไฟล์ {json_file}")
        print("กรุณาตรวจสอบว่าไฟล์อยู่ในโฟลเดอร์เดียวกันกับ script นี้")
    except json.JSONDecodeError:
        print(f"❌ ไฟล์ {json_file} มีรูปแบบ JSON ไม่ถูกต้อง")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {str(e)}")

if __name__ == "__main__":
    print("🔄 เริ่มแปลง JSON เป็น Excel...")
    convert_json_to_excel()
    print("\n✨ เสร็จสิ้น!")
    input("กด Enter เพื่อปิด...")