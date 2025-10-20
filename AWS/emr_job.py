from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("emr-etl").getOrCreate()

df = spark.read.option("header","true").csv("s3://enterprise-bkk-files/STB_TEST_Script/EMR/INPUT/")
df = df.selectExpr(
  "customer_id",
  "cast(quantity as int) as qty",
  "cast(unit_price as double) as price",
  "qty * price as amount"
)
df.write.mode("overwrite").parquet("s3://enterprise-bkk-files/STB_TEST_Script/EMR/OUTPUT/")
print("DONE")
