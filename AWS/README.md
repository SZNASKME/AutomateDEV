# AWS Tools

## ภาพรวม
เครื่องมือสำหรับการทำงานกับบริการ Amazon Web Services (AWS)

## ไฟล์

### csv_to_parquet.py
**วัตถุประสงค์**: แปลงไฟล์ CSV เป็นรูปแบบ Parquet โดยใช้ Apache Spark และ AWS Glue

**ฟีเจอร์หลัก**:
- อ่านไฟล์ CSV พร้อมกับ header และ schema inference
- ทำความสะอาดข้อมูลโดยการตัดช่องว่างในชื่อ column
- เขียนข้อมูลในรูปแบบ Parquet
- รองรับการทำงานบน AWS Glue

**พารามิเตอร์**:
- `JOB_NAME`: ชื่อของ job
- `INPUT_PATH`: path ของไฟล์ CSV input
- `OUTPUT_PATH`: path สำหรับเก็บไฟล์ Parquet output

**วิธีใช้**:
```bash
# ใช้ผ่าน AWS Glue
aws glue start-job-run --job-name your-job-name --arguments='--INPUT_PATH=s3://bucket/input.csv --OUTPUT_PATH=s3://bucket/output/'
```

### emr_job.py
**วัตถุประสงค์**: งานสำหรับ Amazon EMR (Elastic MapReduce)

**คำอธิบาย**: ไฟล์นี้ใช้สำหรับการประมวลผลข้อมูลขนาดใหญ่บน Amazon EMR cluster

## ข้อกำหนด
- AWS Glue SDK
- PySpark
- boto3 (สำหรับการเชื่อมต่อ AWS services)

## การตั้งค่า
1. ตั้งค่า AWS credentials
2. สร้าง IAM role สำหรับ Glue job
3. อัพโหลดสคริปต์ไปยัง S3 bucket