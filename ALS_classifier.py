import findspark
findspark.init()
import time
from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession,Row
from pyspark.sql.functions import col
from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import BinaryClassificationEvaluator


print('loading data...')
# User_id1, User_id2, TimeStamp
sc = SparkContext(conf=SparkConf())
# graph_cb_data = sc.textFile('tweet_data/graph_cb.txt').map(lambda line: line.split(" ")).map(lambda tokens: Row(user=int(tokens[0]),follower=int(tokens[1]),friendship=float(1)))
spark=SparkSession.builder.master("local").appName("tweet_graph_cb").getOrCreate()
df=spark.read.csv('tweet_data/graph_cb_balanced.csv',header=True).select(col('id_scr').alias('follower'),col('id_dst').alias('user'),col('follow').alias('friendship'))

train_col=['user','follower','friendship']

for i in train_col:
    df=df.withColumn(i,df[i].cast('float'))

print('Spliting train and test data...')
training_df, validation_df, test_df = df.randomSplit([0.7, 0.2, 0.1],seed=0)

print('Build ALS model...')
# Modeling-parameter
st=time.time()
seed = 0
iterations = 10
regularization_parameter = 0.1

als = ALS(maxIter=iterations, regParam=regularization_parameter, userCol="user", itemCol="follower", ratingCol="friendship",coldStartStrategy="drop")
model = als.fit(training_df)
ed=time.time()
train_t=ed-st
print('training time is {:.2f} s'.format(train_t))

st=time.time()
pred = model.transform(validation_df)
evals=pred.select(pred.prediction.cast('double').alias('pred'),'friendship')
evals.show(10)
evaluator = BinaryClassificationEvaluator(rawPredictionCol="pred", labelCol="friendship")
print('Area Under ROC:  {:.4f}'.format(evaluator.evaluate(evals)))
ed=time.time()
eval_t=ed-st
print('evaluating time is {:.2f} s'.format(eval_t))