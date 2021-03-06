import pandas as pd
from AwsS3Storage.awsStorageManagement import AwsStorageManagement

class Data_Getter:
    """
    This class shall  be used for obtaining the data from the source for training.

    """
    def __init__(self, file_object, logger_object):
        self.training_file='InputFile.csv'
        self.file_object=file_object
        self.logger_object=logger_object
        self.awsObj = AwsStorageManagement()

    def get_data(self):
        """
        Method Name: get_data
        Description: This method reads the data from source.
        Output: A pandas DataFrame.
        On Failure: Raise Exception

        """
        self.logger_object.log(self.file_object,'Entered the get_data method of the Data_Getter class')
        try:
            print('Loading Dataframe')
            self.data=self.awsObj.csvToDataframe('Training_FileFromDB',self.training_file)
            print('Dataframe Loaded')
            #self.data= pd.read_csv(self.training_file) # reading the data file
            self.logger_object.log(self.file_object,'Data Load Successful.Exited the get_data method of the Data_Getter class')
            return self.data
        except Exception as e:
            self.logger_object.log(self.file_object,'Exception occured in get_data method of the Data_Getter class. Exception message: '+str(e))
            self.logger_object.log(self.file_object,
                                   'Data Load Unsuccessful.Exited the get_data method of the Data_Getter class')
            raise Exception()


