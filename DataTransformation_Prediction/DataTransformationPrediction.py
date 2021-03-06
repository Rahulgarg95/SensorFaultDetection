from datetime import datetime
from os import listdir
import pandas
from application_logging.logger import App_Logger
from AwsS3Storage.awsStorageManagement import AwsStorageManagement

class dataTransformPredict:

     """
                  This class shall be used for transforming the Good Raw Training Data before loading it in Database!!.

                  """

     def __init__(self):
          self.goodDataPath = "Prediction_Good_Raw_Files_Validated"
          self.logger = App_Logger()
          self.awsObj = AwsStorageManagement()

     def replaceMissingWithNull(self):

          """
                                  Method Name: replaceMissingWithNull
                                  Description: This method replaces the missing values in columns with "NULL" to
                                               store in the table. We are using substring in the first column to
                                               keep only "Integer" data for ease up the loading.
                                               This column is anyways going to be removed during prediction.


                                          """

          try:
               #log_file = open("Prediction_Logs/dataTransformLog.txt", 'a+')
               log_file = 'dataTransformLog'
               #onlyfiles = [f for f in listdir(self.goodDataPath)]
               onlyfiles = self.awsObj.listDirFiles(self.goodDataPath)
               #print(onlyfiles)
               for file in onlyfiles:
                    print(file)
                    #csv = pandas.read_csv(self.goodDataPath+"/" + file)
                    csv = self.awsObj.csvToDataframe(self.goodDataPath, file)
                    csv.fillna('NULL',inplace=True)
                    # #csv.update("'"+ csv['Wafer'] +"'")
                    # csv.update(csv['Wafer'].astype(str))
                    csv['Wafer'] = csv['Wafer'].str[6:]
                    self.awsObj.saveDataframeToCsv(self.goodDataPath, file, csv)
                    self.logger.log(log_file," %s: File Transformed successfully!!" % file)
               #log_file.write("Current Date :: %s" %date +"\t" + "Current time:: %s" % current_time + "\t \t" +  + "\n")

          except Exception as e:
               self.logger.log(log_file, "Data Transformation failed because:: %s" % e)
               #log_file.write("Current Date :: %s" %date +"\t" +"Current time:: %s" % current_time + "\t \t" + "Data Transformation failed because:: %s" % e + "\n")
               raise e
