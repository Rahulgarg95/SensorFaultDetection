# SensorFaultDetection
> A classification model built to determine the issues in system given data from multiple sensors.

## Problem Statement
> The inputs of various sensors for different wafers have been provided. In electronics, a wafer (also called a slice or substrate) is a thin slice of semiconductor used for the fabrication of integrated circuits. The goal is to build a machine learning model which predicts whether a wafer needs to be replaced or not(i.e., whether it is working or not) based on the inputs from various sensors. There are two classes: +1 and -1.  
>  1. -1 : Sensor is faulty needs replacement.
>  2. +1 : Sensor in good state.
  
## Key Highlights
>  1. Object Oriented Methodlogy from train to predict.
>  2. Amazon S3 for storage of training files, logs, trained models and all the intermediate files.
>  3. NoSQL MongoDB Altas usage to store all schema details and all training and prediction data.
>  4. Email Alerts for all notifications from training completion to validation results to prediction completion.
>  5. Training and Prediction Pipelines.
>  6. Clustering + Classfication Model Training Approach.
>  7. Dashboard For Interaction with Users.

## Data Validation
>  1. Name Validation.
>  2. Number Of Columns.
>  3. Name Of Columns.
>  4. Datatype Of Columns.
>  5. Null Values in Columns.
  
## Model Training
>  1. Data Export From MongoDB.
>  2. Data Preprocessing.
>  3. Clustering.
>  4. Model Selection.
>  5. Model Storage on Cloud.

## Model Prediction
>  1. Data Export From MongoDB.
>  2. Data Preprocessing.
>  3. Clustering.
>  4. Prediction based on deployed Models.
>  5. Predictions stored in CSV.
