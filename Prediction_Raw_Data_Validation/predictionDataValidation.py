import sqlite3
from datetime import datetime
from os import listdir
import os
import re
import json
import shutil
import pandas as pd
from application_logging.logger import App_Logger
from AwsS3Storage.awsStorageManagement import AwsStorageManagement
from MongoDB.mongoDbDatabase import mongoDBOperation



class Prediction_Data_validation:
    """
               This class shall be used for handling all the validation done on the Raw Prediction Data!!.

               """

    def __init__(self,path):
        self.Batch_Directory = path
        self.schema_path = 'schema_prediction.json'
        self.logger = App_Logger()
        self.awsObj = AwsStorageManagement()
        self.dbObj = mongoDBOperation()

    def valuesFromSchema(self):
        """
                                Method Name: valuesFromSchema
                                Description: This method extracts all the relevant information from the pre-defined "Schema" file.
                                Output: LengthOfDateStampInFile, LengthOfTimeStampInFile, column_names, Number of Columns
                                On Failure: Raise ValueError,KeyError,Exception

                                        """
        try:
            dic=self.dbObj.getRecords('waferFaultDB','predict_schema')
            pattern = dic['SampleFileName']
            LengthOfDateStampInFile = dic['LengthOfDateStampInFile']
            LengthOfTimeStampInFile = dic['LengthOfTimeStampInFile']
            column_names = dic['ColName']
            NumberofColumns = dic['NumberofColumns']

            #file = open("Training_Logs/valuesfromSchemaValidationLog.txt", 'a+')
            file = 'valuesfromSchemaValidationLog'
            message ="LengthOfDateStampInFile:: %s" %LengthOfDateStampInFile + "\t" + "LengthOfTimeStampInFile:: %s" % LengthOfTimeStampInFile +"\t " + "NumberofColumns:: %s" % NumberofColumns + "\n"
            self.logger.log(file,message)

        except ValueError:
            #file = open("Prediction_Logs/valuesfromSchemaValidationLog.txt", 'a+')
            file = 'valuesfromSchemaValidationLog'
            self.logger.log(file,"ValueError:Value not found inside schema_training.json")
            raise ValueError

        except KeyError:
            #file = open("Prediction_Logs/valuesfromSchemaValidationLog.txt", 'a+')
            file = 'valuesfromSchemaValidationLog'
            self.logger.log(file, "KeyError:Key value error incorrect key passed")
            raise KeyError

        except Exception as e:
            #file = open("Prediction_Logs/valuesfromSchemaValidationLog.txt", 'a+')
            file = 'valuesfromSchemaValidationLog'
            self.logger.log(file, str(e))
            raise e

        return LengthOfDateStampInFile, LengthOfTimeStampInFile, column_names, NumberofColumns


    def manualRegexCreation(self):

        """
                                      Method Name: manualRegexCreation
                                      Description: This method contains a manually defined regex based on the "FileName" given in "Schema" file.
                                                  This Regex is used to validate the filename of the prediction data.
                                      Output: Regex pattern
                                      On Failure: None

                                              """
        regex = "['wafer']+['\_'']+[\d_]+[\d]+\.csv"
        return regex

    def createDirectoryForGoodBadRawData(self):

        """
                                        Method Name: createDirectoryForGoodBadRawData
                                        Description: This method creates directories to store the Good Data and Bad Data
                                                      after validating the prediction data.

                                        Output: None
                                        On Failure: OSError

                                                """
        try:
            self.awsObj.createS3Directory('Prediction_Good_Raw_Files_Validated')
            self.awsObj.createS3Directory('Prediction_Bad_Raw_Files_Validated')

        except OSError as ex:
            #file = open("Prediction_Logs/GeneralLog.txt", 'a+')
            file = 'GeneralLog'
            self.logger.log(file,"Error while creating Directory %s:" % ex)
            raise OSError

    def deleteExistingGoodDataTrainingFolder(self):
        """
                                            Method Name: deleteExistingGoodDataTrainingFolder
                                            Description: This method deletes the directory made to store the Good Data
                                                          after loading the data in the table. Once the good files are
                                                          loaded in the DB,deleting the directory ensures space optimization.
                                            Output: None
                                            On Failure: OSError

                                                    """
        try:
            path = 'Prediction_Raw_Files_Validated/'
            #file = open("Prediction_Logs/GeneralLog.txt", 'a+')
            file = 'GeneralLog'
            self.logger.log(file,"GoodRaw directory deleted successfully!!!")
            self.awsObj.deleteDirectory('Prediction_Good_Raw_Files_Validated')
        except OSError as s:
            #file = open("Prediction_Logs/GeneralLog.txt", 'a+')
            file = 'GeneralLog'
            self.logger.log(file,"Error while Deleting Directory : %s" %s)
            raise OSError

    def deleteExistingBadDataTrainingFolder(self):

        """
                                            Method Name: deleteExistingBadDataTrainingFolder
                                            Description: This method deletes the directory made to store the bad Data.
                                            Output: None
                                            On Failure: OSError

                                                    """

        try:
            path = 'Prediction_Raw_Files_Validated/'
            #file = open("Prediction_Logs/GeneralLog.txt", 'a+')
            file = 'GeneralLog'
            self.logger.log(file,"BadRaw directory deleted before starting validation!!!")
            self.awsObj.deleteDirectory('Prediction_Bad_Raw_Files_Validated')
        except OSError as s:
            #file = open("Prediction_Logs/GeneralLog.txt", 'a+')
            file = 'GeneralLog'
            self.logger.log(file,"Error while Deleting Directory : %s" %s)
            raise OSError

    def moveBadFilesToArchiveBad(self):


        """
                                            Method Name: moveBadFilesToArchiveBad
                                            Description: This method deletes the directory made  to store the Bad Data
                                                          after moving the data in an archive folder. We archive the bad
                                                          files to send them back to the client for invalid data issue.
                                            Output: None
                                            On Failure: OSError

                                                    """
        now = datetime.now()
        date = now.date()
        time = now.strftime("%H%M%S")
        try:
            target_folder = 'PredictionArchivedBadData/BadData_' + str(date) + "_" + str(time)
            self.awsObj.copyFileToFolder('Prediction_Bad_Raw_Files_Validated', target_folder)

            #file = open("Prediction_Logs/GeneralLog.txt", 'a+')
            file = 'GeneralLog'
            self.logger.log(file,"Bad files moved to archive")

            self.logger.log(file,"Bad Raw Data Folder Deleted successfully!!")

        except OSError as e:
            #file = open("Prediction_Logs/GeneralLog.txt", 'a+')
            file = 'GeneralLog'
            self.logger.log(file, "Error while moving bad files to archive:: %s" % e)
            raise OSError




    def validationFileNameRaw(self,regex,LengthOfDateStampInFile,LengthOfTimeStampInFile):
        """
            Method Name: validationFileNameRaw
            Description: This function validates the name of the prediction csv file as per given name in the schema!
                         Regex pattern is used to do the validation.If name format do not match the file is moved
                         to Bad Raw Data folder else in Good raw data.
            Output: None
            On Failure: Exception

        """
        # delete the directories for good and bad data in case last run was unsuccessful and folders were not deleted.
        self.deleteExistingBadDataTrainingFolder()
        self.deleteExistingGoodDataTrainingFolder()
        self.createDirectoryForGoodBadRawData()
        batch_dir=self.Batch_Directory.strip('/').strip('\\')
        print('Prediction File Path: ',batch_dir)
        #self.awsObj.uploadFiles(batch_dir,batch_dir)
        onlyfiles = self.awsObj.listDirFiles(batch_dir)
        #onlyfiles = [f for f in listdir(self.Batch_Directory)]
        try:
            #f = open("Prediction_Logs/nameValidationLog.txt", 'a+')
            f = 'nameValidationLog'
            for filename in onlyfiles:
                if (re.match(regex, filename)):
                    splitAtDot = re.split('.csv', filename)
                    splitAtDot = (re.split('_', splitAtDot[0]))
                    if len(splitAtDot[1]) == LengthOfDateStampInFile:
                        if len(splitAtDot[2]) == LengthOfTimeStampInFile:
                            self.awsObj.copyFileToFolder(batch_dir, 'Prediction_Good_Raw_Files_Validated',
                                                         filename)
                            self.logger.log(f,"Valid File name!! File moved to GoodRaw Folder :: %s" % filename)

                        else:
                            self.awsObj.copyFileToFolder(self.Batch_Directory, 'Prediction_Bad_Raw_Files_Validated',
                                                         filename)
                            self.logger.log(f,"Invalid File Name!! File moved to Bad Raw Folder :: %s" % filename)
                    else:
                        self.awsObj.copyFileToFolder(self.Batch_Directory, 'Prediction_Bad_Raw_Files_Validated',
                                                     filename)
                        self.logger.log(f,"Invalid File Name!! File moved to Bad Raw Folder :: %s" % filename)
                else:
                    self.awsObj.copyFileToFolder(self.Batch_Directory, 'Prediction_Bad_Raw_Files_Validated',
                                                 filename)
                    self.logger.log(f, "Invalid File Name!! File moved to Bad Raw Folder :: %s" % filename)

        except Exception as e:
            #f = open("Prediction_Logs/nameValidationLog.txt", 'a+')
            f = 'nameValidationLog'
            self.logger.log(f, "Error occured while validating FileName %s" % e)
            raise e




    def validateColumnLength(self,NumberofColumns):
        """
                    Method Name: validateColumnLength
                    Description: This function validates the number of columns in the csv files.
                                 It is should be same as given in the schema file.
                                 If not same file is not suitable for processing and thus is moved to Bad Raw Data folder.
                                 If the column number matches, file is kept in Good Raw Data for processing.
                                The csv file is missing the first column name, this function changes the missing name to "Wafer".
                    Output: None
                    On Failure: Exception

             """
        try:
            #f = open("Prediction_Logs/columnValidationLog.txt", 'a+')
            f = 'columnValidationLog'
            self.logger.log(f,"Column Length Validation Started!!")
            file_list = self.awsObj.listDirFiles('Prediction_Good_Raw_Files_Validated')
            for file in file_list:
                csv = self.awsObj.csvToDataframe('Prediction_Good_Raw_Files_Validated',file)
                if csv.shape[1] == NumberofColumns:
                    csv.rename(columns={"Unnamed: 0": "Wafer"}, inplace=True)
                    #csv.to_csv("Prediction_Raw_Files_Validated/Good_Raw/" + file, index=None, header=True)
                    self.awsObj.saveDataframeToCsv('Prediction_Good_Raw_Files_Validated', file, csv)
                else:
                    self.awsObj.moveFileToFolder('Prediction_Good_Raw_Files_Validated',
                                                 'Prediction_Bad_Raw_Files_Validated', file)
                    self.logger.log(f, "Invalid Column Length for the file!! File moved to Bad Raw Folder :: %s" % file)

            self.logger.log(f, "Column Length Validation Completed!!")
        except OSError:
            #f = open("Prediction_Logs/columnValidationLog.txt", 'a+')
            f = 'columnValidationLog'
            self.logger.log(f, "Error Occured while moving the file :: %s" % OSError)
            raise OSError
        except Exception as e:
            #f = open("Prediction_Logs/columnValidationLog.txt", 'a+')
            f = 'columnValidationLog'
            self.logger.log(f, "Error Occured:: %s" % e)
            raise e

    def deletePredictionFile(self):

        self.awsObj.deleteFile('Prediction_Output_File','Predictions.csv')

    def validateMissingValuesInWholeColumn(self):
        """
                                  Method Name: validateMissingValuesInWholeColumn
                                  Description: This function validates if any column in the csv file has all values missing.
                                               If all the values are missing, the file is not suitable for processing.
                                               SUch files are moved to bad raw data.
                                  Output: None
                                  On Failure: Exception

                              """
        try:
            #f = open("Prediction_Logs/missingValuesInColumn.txt", 'a+')
            f = 'missingValuesInColumn'
            self.logger.log(f, "Missing Values Validation Started!!")
            file_list = self.awsObj.listDirFiles('Prediction_Good_Raw_Files_Validated')
            for file in file_list:
                csv = self.awsObj.csvToDataframe('Prediction_Good_Raw_Files_Validated', file)
                count = 0
                for columns in csv:
                    if (len(csv[columns]) - csv[columns].count()) == len(csv[columns]):
                        count+=1
                        self.awsObj.moveFileToFolder('Prediction_Good_Raw_Files_Validated',
                                                     'Prediction_Bad_Raw_Files_Validated', file)
                        self.logger.log(f,"Invalid Column Length for the file!! File moved to Bad Raw Folder :: %s" % file)
                        break
                if count==0:
                    csv.rename(columns={"Unnamed: 0": "Wafer"}, inplace=True)
                    self.awsObj.saveDataframeToCsv('Prediction_Good_Raw_Files_Validated', file, csv)
        except OSError:
            #f = open("Prediction_Logs/missingValuesInColumn.txt", 'a+')
            f = 'missingValuesInColumn'
            self.logger.log(f, "Error Occured while moving the file :: %s" % OSError)
            raise OSError
        except Exception as e:
            #f = open("Prediction_Logs/missingValuesInColumn.txt", 'a+')
            f = 'missingValuesInColumn'
            self.logger.log(f, "Error Occured:: %s" % e)
            raise e