import pandas as pd
import pymongo
import json

class mongoDBOperation:
    def __init__(self):
        self.mongouser='Mongo User'
        self.mongopasswd='Mongo Passwd'
        self.connstr="mongodb+srv://{}:{}@python-mongo.enkic.mongodb.net/waferFaultDB?retryWrites=true&w=majority".format(self.mongouser,self.mongopasswd)
        #self.connstr='mongodb://localhost:27017/'

    def connectMongoClient(self):
        client = pymongo.MongoClient(self.connstr)
        return client

    def isDbPresent(self,db_name):
        client=self.connectMongoClient()
        if db_name in client.list_database_names():
            client.close()
            return True
        else:
            client.close()
            return False

    def createOrGetCollection(self,db_name,collection_name):
        client = self.connectMongoClient()
        db = client[db_name]
        collection = db[collection_name]
        return collection

    def isCollectionPresent(self,db_name,collection_name):
        client=self.connectMongoClient()
        db=client[db_name]
        if collection_name in db.list_collection_names():
            client.close()
            return True
        else:
            client.close()
            return False

    def insertOneRecord(self,db_name,collection_name,record):
        collection=self.createOrGetCollection(db_name,collection_name)
        collection.insert_one(record)

    def insertManyRecords(self,db_name,collection_name,records):
        collection=self.createOrGetCollection(db_name,collection_name)
        collection.insert_many(records)


    def isRecordPresent(self,db_name,collection_name,records):
        collection=self.createOrGetCollection(db_name,collection_name)
        record_data=collection.find(records)
        if record_data.count() > 0:
            return False
        else:
            return True

    def dataframeToRecords(self,db_name,collection_name,data):
        records = list(json.loads(data.T.to_json()).values())
        self.insertManyRecords(db_name,collection_name,records)

    def recordsToDataFrame(self,db_name,collection_name):
        collection=self.createOrGetCollection(db_name,collection_name)
        tmp_df=pd.DataFrame(list(collection.find()))
        if '_id' in tmp_df:
            tmp_df=tmp_df.drop('_id',axis=1)
        return tmp_df

    def dropCollection(self,db_name,collection_name):
        if self.isCollectionPresent(db_name,collection_name):
            collection=self.createOrGetCollection(db_name,collection_name)
            collection.drop()

    def getRecords(self,db_name,collection_name):
        if self.isCollectionPresent(db_name, collection_name):
            collection = self.createOrGetCollection(db_name, collection_name)
            records=collection.find()
            if records.count()==1:
                for record in records:
                    return record
            elif records.count()>1:
                record_l=[]
                for record in records:
                    record_l.append(record)
                return record_l
            else:
                return None