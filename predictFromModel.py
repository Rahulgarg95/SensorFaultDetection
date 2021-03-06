import pandas
from file_operations import file_methods
from data_preprocessing import preprocessing
from data_ingestion import data_loader_prediction
from application_logging import logger
from Prediction_Raw_Data_Validation.predictionDataValidation import Prediction_Data_validation
from AwsS3Storage.awsStorageManagement import AwsStorageManagement
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from Email_Trigger.send_email import email
from datetime import datetime

class prediction:

    def __init__(self,path):
        #self.file_object = open("Prediction_Logs/Prediction_Log.txt", 'a+')
        self.file_object = 'Prediction_Log'
        self.log_writer = logger.App_Logger()
        self.awsObj = AwsStorageManagement()
        self.emailObj = email()
        if path is not None:
            self.pred_data_val = Prediction_Data_validation(path)

    def predictionFromModel(self):

        try:
            self.pred_data_val.deletePredictionFile() #deletes the existing prediction file from last run!
            self.log_writer.log(self.file_object,'Start of Prediction')
            data_getter=data_loader_prediction.Data_Getter_Pred(self.file_object,self.log_writer)
            data=data_getter.get_data()

            #code change
            # wafer_names=data['Wafer']
            # data=data.drop(labels=['Wafer'],axis=1)

            preprocessor=preprocessing.Preprocessor(self.file_object,self.log_writer)
            is_null_present=preprocessor.is_null_present(data)
            if(is_null_present):
                data=preprocessor.impute_missing_values(data)

            print('Impute Missing Values Done')
            cols_to_drop=preprocessor.get_columns_with_zero_std_deviation(data)
            print('Col Zero Std deviation')
            data=preprocessor.remove_columns(data,cols_to_drop)
            print('Remove columns Function')
            #data=data.to_numpy()
            file_loader=file_methods.File_Operation(self.file_object,self.log_writer)
            print('Finding KMeans Model Load')
            kmeans=file_loader.load_model('KMeans')
            print('Finding KMeans Model Load DOne')

            ##Code changed
            #pred_data = data.drop(['Wafer'],axis=1)
            clusters=kmeans.predict(data.drop(['Wafer'],axis=1))#drops the first column for cluster prediction
            data['clusters']=clusters
            clusters=data['clusters'].unique()
            for i in clusters:
                cluster_data= data[data['clusters']==i]
                wafer_names = list(cluster_data['Wafer'])
                cluster_data=data.drop(labels=['Wafer'],axis=1)
                cluster_data = cluster_data.drop(['clusters'],axis=1)
                model_name = file_loader.find_correct_model_file(i)
                model = file_loader.load_model(model_name)
                result=list(model.predict(cluster_data))
                result = pandas.DataFrame(list(zip(wafer_names,result)),columns=['Wafer','Prediction'])
                path="Prediction_Output_File/Predictions.csv"
                if i==0:
                    final_result=result.copy()
                else:
                    final_result=pandas.concat([final_result,result.copy()])
                self.awsObj.saveDataframeToCsv('Prediction_Output_File','Predictions.csv',final_result)
                print('Final Prediction Saved')
                #result.to_csv("Prediction_Output_File/Predictions.csv",header=True,mode='a+') #appends result to prediction file
            self.log_writer.log(self.file_object,'End of Prediction')
            msg = MIMEMultipart()
            msg['Subject'] = 'WaferFaultDetection - Prediction Done | ' + str(datetime.now())
            body = 'Model Prediction Done Successfully... <br><br> Thanks and Regards, <br> Rahul Garg'
            msg.attach(MIMEText(body, 'html'))
            to_addr=['rahulgarg366@gmail.com']
            self.emailObj.trigger_mail(to_addr,[],msg)
        except Exception as ex:
            self.log_writer.log(self.file_object, 'Error occured while running the prediction!! Error:: %s' % ex)
            raise ex
        return path, result.head().to_json(orient="records")