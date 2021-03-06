import os
import pandas as pd
import boto3
import io
from application_logging.logger import App_Logger

class AwsStorageManagement:

    def __init__(self):
        self.AWS_KEY_ID = 'Please enter key id'  # AWS KEY ID
        self.AWS_SECRET = 'Please enter secret Key'  # AWS SECRET KEY

        #Creating a s3 client to access resources
        self.s3 = boto3.client("s3",
                          region_name='ap-south-1',
                          aws_access_key_id=self.AWS_KEY_ID,
                          aws_secret_access_key=self.AWS_SECRET)

        #Create a resource object
        self.res_s3 = boto3.resource('s3',
                                    region_name='ap-south-1',
                                    aws_access_key_id=self.AWS_KEY_ID,
                                    aws_secret_access_key=self.AWS_SECRET)
        #self.bucket_name='sensor-fault-detection'
        self.bucket_name = 'sensorfaultdetection'
        self.logger = App_Logger()
        #self.file = open("Training_Logs/awsBucketManagementLogs.txt", 'a+')
        self.file = 'awsBucketManagementLogs'

    def isFolderPresent(self,folder_name):
        """
        :param folder_name: folder_name to search in bucket
        :return: True if given folder_name is present in AWS S3
        """
        contents=self.s3.list_objects(Bucket=self.bucket_name,Delimiter='/')['CommonPrefixes']
        for data in contents:
            if folder_name in data['Prefix']:
                return True
        else:
            return False

    def isFilePresent(self,folder_name,file_name):
        """
        :param folder_name: Folder name in which file to be checked
        :param file_name: File Name to be checked
        :return: Return status of presence of given file
        """
        contents=self.s3.list_objects(Bucket=self.bucket_name,Prefix=folder_name+'/')['Contents']
        for data in contents:
            if file_name in data['Key']:
                return True
            else:
                return False

    def createS3Directory(self,folder_name):
        """

        :param folder_name: folder name to be create
        :return: None
        """
        if self.isFolderPresent(folder_name):
            message='Folder: ' + folder_name + ' already present in bucket'
            self.logger.log(self.file,message)
        else:
            self.s3.put_object(Bucket=self.bucket_name, Key=(folder_name+'/'))
            message = 'Required Folder: ' + folder_name + ' created'
            self.logger.log(self.file, message)

    def uploadFiles(self,source_dir,dest_dir,file_name=''):
        """
        :param source_dir: Folder in local system from where file to be uploaded
        :param dest_dir: Folder in S3 bucket to which file to be uploaded
        :param file_name: File to be uploaded
        :return:
        """
        if not self.isFolderPresent(dest_dir):
            self.createS3Directory(dest_dir)
        if file_name == '':
            message='Single File Not provided hence bulk upload mode'
            self.logger.log(self.file, message)
            file_list=os.listdir(source_dir)
            for file_n in file_list:
                if not self.isFilePresent(dest_dir,file_n):
                    self.s3.upload_file(os.path.join(source_dir,file_n), self.bucket_name,dest_dir+'/'+file_n)
            self.logger.log(self.file, 'Bulk file upload done')
        else:
            self.s3.upload_file(os.path.join(source_dir, file_name), self.bucket_name, dest_dir+'/'+file_name)

    def csvToDataframe(self,folder_name,file_name=''):
        """

        :param folder_name:
        :param file_name:
        :return: Returns dataframe
        """
        if file_name == '':
            message='File Name Not Provided, loading all files from ' + folder_name + ' to dataframe'
            self.logger.log(self.file,message)
            response = self.s3.list_objects(Bucket=self.bucket_name, Prefix=folder_name+"/")
            request_files = response["Contents"]
            cnt=0
            for file in request_files:
                if '.csv' in file['Key']:
                    #print(file['Key'])
                    obj = self.s3.get_object(Bucket=self.bucket_name, Key=file["Key"])
                    tmp_df = pd.read_csv(io.BytesIO(obj['Body'].read()))
                    print(tmp_df.columns)
                    if cnt==0:
                        obj_df=tmp_df.copy()
                        cnt+=1
                    else:
                        obj_df=pd.concat([obj_df,tmp_df])
            message='Dataframe created from folder: ' + folder_name + '.Total Records: ' + str(obj_df.shape[0]) + ' Total Columns: ' + str(obj_df.shape[0])
            self.logger.log(self.file, message)
            return obj_df
        else:
            obj = self.s3.get_object(Bucket=self.bucket_name, Key=folder_name+'/'+file_name)
            obj_df = pd.read_csv(io.BytesIO(obj['Body'].read()))
            return obj_df

    def saveObject(self,folder_name,file_name,object_name,content_type):
        """

        :param folder_name: Folder name to be accessed
        :param file_name: File to be created
        :param object_name: Object to be loaded
        :return: None
        """
        self.s3.put_object(Body=object_name, Bucket=self.bucket_name,ContentType=content_type,
                      Key=folder_name+'/'+file_name)
        message='Object Loaded to File: ' + file_name
        self.logger.log(self.file, message)

    def loadObject(self,folder_name,file_name):
        """

        :param folder_name: Folder containing file
        :param file_name: File to be loaded
        :return: object loaded
        """
        obj = self.s3.get_object(Bucket=self.bucket_name, Key=folder_name+'/'+file_name)
        object_name=obj['Body'].read()
        return object_name

    def listDirFiles(self,folder_name):
        """

        :param folder_name: Folder from which files to be listed
        :return: list with file_names
        """
        response = self.s3.list_objects(Bucket=self.bucket_name, Prefix=folder_name + "/")
        request_files = response["Contents"]
        file_list=[]
        for file in request_files:
            if not file['Key'].split('/')[-1]=='':
                file_n=file['Key'].split('/')[-1]
                file_list.append(file_n)
        return file_list

    def copyFileToFolder(self,source_folder,target_folder,file_name=''):
        """

        :param source_folder: Copy files from dir
        :param target_folder: Copy files to dir
        :param file_name: File_name
        :return:
        """
        if file_name=='':
            file_list=self.listDirFiles(source_folder)
            for file_n in file_list:
                print(file_n)
                copy_source = {
                    'Bucket': self.bucket_name,
                    'Key': source_folder+'/'+file_n
                }
                self.s3.copy(copy_source, self.bucket_name, target_folder+'/'+file_n)
        else:
            copy_source = {
                'Bucket': self.bucket_name,
                'Key': source_folder+'/'+file_name
            }
            self.s3.copy(copy_source, self.bucket_name, target_folder+'/'+file_name)

    def deleteFile(self,folder_name,file_name=''):
        """

        :param folder_name: Folder Name containing files to delete
        :param file_name: File Name to delete
        :return: None
        """
        if file_name=='':
            file_list = self.listDirFiles(folder_name)
            for file_n in file_list:
                self.s3.delete_object(Bucket=self.bucket_name,Key=folder_name+'/'+file_n)
        else:
            self.s3.delete_object(Bucket=self.bucket_name, Key=folder_name+'/'+file_name)

    def deleteDirectory(self,folder_name):
        """

        :param folder_name:
        :return:
        """
        bucket_n = self.res_s3.Bucket(self.bucket_name)
        if self.isFolderPresent(folder_name):
            bucket_n.objects.filter(Prefix=folder_name+'/').delete()

    def moveFileToFolder(self, source_folder, target_folder, file_name=''):
        """

        :param source_folder:
        :param target_folder:
        :param file_name:
        :return:
        """
        if file_name=='':
            self.copyFileToFolder(source_folder,target_folder)
            self.deleteFile(source_folder)
        else:
            self.copyFileToFolder(source_folder, target_folder,file_name)
            self.deleteFile(source_folder,file_name)



    def saveDataframeToCsv(self,folder_name,file_name,df):
        """

        :param folder_name: Folder Name where file needs to be placed
        :param file_name: File Name to which dataframe is stored
        :param df: Dataframe to be loaded
        :return: None
        """
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer,index=False)
        self.res_s3.Object(self.bucket_name, folder_name+'/'+file_name).put(Body=csv_buffer.getvalue())
