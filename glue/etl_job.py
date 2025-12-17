import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, expr

args = getResolvedOptions(
    sys.argv,
    ['JOB_NAME', 'S3_BUCKET', 'S3_KEY']
)

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Event-driven based S3 read
input_path = f"s3://{args['S3_BUCKET']}/{args['S3_KEY']}"

raw_df = (
    spark.read
    .option("header", "true")
    .csv(input_path)
)

# Data cleaning
clean_df = raw_df.dropna()

# Type casting
typed_df = (
    clean_df
    .withColumn("quantity", col("quantity").cast("int"))
    .withColumn("price", col("price").cast("double"))
)

# Business transformation
final_df = typed_df.withColumn(
    "total_amount",
    expr("quantity * price")
)

# Write to Processed zone in Parquet format
(
    final_df
    .write
    .mode("append")
    .partitionBy("order_date")
    .parquet("s3://sales-datalake-processed-etl/sales/orders/")
)

job.commit()
