import shutil
import sqlite3
from datetime import datetime
from os import listdir
import os
import csv
from application_logging.logger import App_Logger
from MongoDB.mongoDbDatabase import mongoDBOperation
from AwsS3Storage.awsStorageManagement import AwsStorageManagement


class dBOperation:
    """
      This class shall be used for handling all the SQL operations.

      Written By: iNeuron Intelligence
      Version: 1.0
      Revisions: None

      """
    def __init__(self):
        self.path = 'Training_Database/'
        self.badFilePath = "Training_Bad_Raw_Files_Validated"
        self.goodFilePath = "Training_Good_Raw_Files_Validated"
        self.logger = App_Logger()
        self.awsObj = AwsStorageManagement()
        self.dbObj = mongoDBOperation()

    def createTableDb(self,DatabaseName,column_names):
        """
                        Method Name: createTableDb
                        Description: This method creates a table in the given database which will be used to insert the Good data after raw data validation.
                        Output: None
                        On Failure: Raise Exception
                        """
        try:
                self.dbObj.createOrGetCollection('waferFaultDB','Good_Raw_Data')

                #file = open("Training_Logs/DbTableCreateLog.txt", 'a+')
                file = 'DbTableCreateLog'
                self.logger.log(file, "Tables created successfully!!")

                #file = open("Training_Logs/DataBaseConnectionLog.txt", 'a+')
                file = 'DataBaseConnectionLog'
                self.logger.log(file, "Closed %s database successfully" % DatabaseName)

        except Exception as e:
            #file = open("Training_Logs/DbTableCreateLog.txt", 'a+')
            file = 'DbTableCreateLog'
            self.logger.log(file, "Error while creating table: %s " % e)

            #file = open("Training_Logs/DataBaseConnectionLog.txt", 'a+')
            file = 'DataBaseConnectionLog'
            self.logger.log(file, "Closed %s database successfully" % DatabaseName)
            raise e


    def insertIntoTableGoodData(self,Database):

        """
                               Method Name: insertIntoTableGoodData
                               Description: This method inserts the Good data files from the Good_Raw folder into the
                                            above created table.
                               Output: None
                               On Failure: Raise Exception

        """

        #conn = self.dataBaseConnection(Database)
        goodFilePath= self.goodFilePath
        badFilePath = self.badFilePath
        onlyfiles = self.awsObj.listDirFiles(goodFilePath)
        #log_file = open("Training_Logs/DbInsertLog.txt", 'a+')
        log_file = 'DbInsertLog'
        self.dbObj.dropCollection('waferFaultDB','Good_Raw_Data')

        for file in onlyfiles:
            try:
                df_csv = self.awsObj.csvToDataframe(self.goodFilePath, file)
                self.dbObj.dataframeToRecords('waferFaultDB','Good_Raw_Data',df_csv)

            except Exception as e:
                self.logger.log(log_file,"Error while creating table: %s " % e)
                self.awsObj.moveFileToFolder(goodFilePath, badFilePath, file)
                self.logger.log(log_file, "File Moved Successfully %s" % file)
        print('Data pushed to mongodb...')


    def selectingDatafromtableintocsv(self,Database):

        """
                               Method Name: selectingDatafromtableintocsv
                               Description: This method exports the data in GoodData table as a CSV file. in a given location.
                                            above created .
                               Output: None
                               On Failure: Raise Exception

        """

        self.fileFromDb = 'Training_FileFromDB'
        self.fileName = 'InputFile.csv'
        self.awsObj.createS3Directory(self.fileFromDb)
        #log_file = open("Training_Logs/ExportToCsv.txt", 'a+')
        log_file = 'ExportToCsv'
        try:
            tmp_csv = self.dbObj.recordsToDataFrame(Database,'Good_Raw_Data')
            tmp_csv = tmp_csv.rename(columns={'Good/Bad':'Output'})
            self.awsObj.saveDataframeToCsv('Training_FileFromDB',self.fileName,tmp_csv)

            self.logger.log(log_file, "File exported successfully!!!")
            print('Saving data to final csv')

        except Exception as e:
            self.logger.log(log_file, "File exporting failed. Error : %s" %e)