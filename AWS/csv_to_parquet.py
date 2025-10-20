import sys
from pyspark.sql import SparkSession
from awsglue.utils import getResolvedOptions

args = getResolvedOptions(sys.argv, ["JOB_NAME", "INPUT_PATH", "OUTPUT_PATH"])
spark = SparkSession.builder.getOrCreate()

# อ่าน CSV (เดมินิ, header)
df = spark.read.option("header", "true").option("inferSchema", "true").csv(args["INPUT_PATH"])

# ตัวอย่างแปลง: ตัดช่องว่าง และแปลงเป็นพิมพ์เล็กบางคอลัมน์ถ้ามี
for c in df.columns:
    df = df.withColumnRenamed(c, c.strip())

# เขียนเป็น Parquet (overwrite)
df.write.mode("overwrite").parquet(args["OUTPUT_PATH"])

print("DONE")
