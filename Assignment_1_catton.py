# Indigo Catton
# CS777 Assignment 1
from __future__ import print_function

import os
import sys
import requests
from operator import add

from pyspark import SparkConf,SparkContext
from pyspark.streaming import StreamingContext

from pyspark.sql import SparkSession

from pyspark.sql.types import *
from pyspark.sql import functions as func
from pyspark.sql.functions import *


#Exception Handling and removing wrong datalines
def isfloat(value):
    try:
        float(value)
        return True
 
    except:
         return False

#Function - Cleaning
#For example, remove lines if they don't have 16 values and 
# checking if the trip distance and fare amount is a float number
# checking if the trip duration is more than a minute, trip distance is more than 0 miles, 
# fare amount and total amount are more than 0 dollars
def correctRows(p):
    if(len(p)==17):
        if(isfloat(p[5]) and isfloat(p[11])):
            if(float(p[4])> 60 and float(p[5])>0 and float(p[11])> 0 and float(p[16])> 0):
                return p

#Main
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: main_task1 <file> <output> ", file=sys.stderr)
        exit(-1)
    

    sc = SparkContext(appName="Assignment-1")

    rdd = sc.textFile(sys.argv[1]).map(lambda line: line.split(','))
    
    # clean input rows
    taxilinesCorrected = rdd.filter(correctRows)
    
    #Task 1
    # value of 1 for each taxi driver combination
    driver_taxi = taxilinesCorrected.map(lambda x : (x[0], x[1])).distinct()    
    taxi_counts = driver_taxi.map(lambda x : (x[0], 1))    
    
    # value counts number of drivers per taxi
    counts = taxi_counts.reduceByKey(add)
    
    # get top 10 values
    top = counts.top(10, lambda x:x[1])
    
    # save output
    out_1 = sc.parallelize(top).coalesce(1)
    out_1.saveAsTextFile(sys.argv[2])
    

    #Task 2
    # Get required values convert time to min
    rides = taxilinesCorrected.map(lambda x : (x[1], (float(x[11]), (float(x[4])/60)))) 
    # Add all fares and time per driver
    driver_sum = rides.reduceByKey(lambda x, y: (x[0]+ y[0], x[1]+ y[1]))
    # Calculate average cost per minute
    driver_avg = driver_sum.map(lambda x: (x[0], x[1][0] / x[1][1]))

    # drivers with highest average fare per minute
    top_rate = driver_avg.top(10, key = lambda x: x[1])
    print(top_rate)
    # Save output to argument
    out_2 = sc.parallelize(top_rate).coalesce(1)
    out_2.saveAsTextFile(sys.argv[2])

    sc.stop()
