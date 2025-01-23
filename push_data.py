import os 
import sys
import json

from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL=os.getenv("MONGO_DB_URL")
print(MONGO_DB_URL)

import certifi
#Certifcate Authority (CA) Bundle
ca=certifi.where()# Provides sets of root certificates for use by SSL

import pandas as pd
import numpy as np
import pymongo
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

class NetworkDataExtract():
    def __init__(self):
        try:
            pass
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def cv_to_json_converter(self,file_path):
        try:
            data=pd.read_csv(file_path)
            data.reset_index(drop=True,inplace=True)# Reset the index of the DataFrame, and use the default one instead
            # Convert the data to a dictionary , for ex:[{},{}]
            records=list(json.loads(data.T.to_json()).values()) # T is the transpose of the DataFrame, to_json() converts the DataFrame to a JSON string, and json.loads() converts the JSON string to a dictionary
            return records
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def insert_data_mongodb(self, records, database, collection):
        try:
            self.database=database
            self.collection=collection
            self.records=records

            self.mongo_client=pymongo.MongoClient(MONGO_DB_URL) # Create a new client and connect to the server
            self.database=self.mongo_client[self.database] # Access the database
            
            self.collection=self.database[self.collection] # Access the collection
            self.collection.insert_many(self.records) # Insert the records into the collection
            return (len(self.records))
        
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
if __name__ == "__main__":
    FILE_PATH="Network_Data\phisingData.csv"
    DATABASE="TestNetSec"
    
    Collection="NetworkData"
    networkobj=NetworkDataExtract()
    print(FILE_PATH)
    
    records=networkobj.cv_to_json_converter(FILE_PATH)
    print(records)

    no_of_records=networkobj.insert_data_mongodb(records, DATABASE, Collection)
    print(no_of_records)
