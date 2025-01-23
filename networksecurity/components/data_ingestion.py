from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

## Call the configuration of the data ingestion Config
from networksecurity.entity.config_entity import DataIngestionConfig

from networksecurity.entity.artifact_entity import DataIngestionArtifact

import os
import sys
import numpy as np
import pandas as pd
import pymongo
from typing import List

from sklearn.model_selection import train_test_split

from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")

class DataIngestion:
    def __init__(self, data_ingestion_config:DataIngestionConfig):
        try:
            self.data_ingestion_config=data_ingestion_config

        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def export_collection_as_dataframe(self):
        """
            Export the collection from the MongoDB as a dataframe
        """
        try:
            database_name=self.data_ingestion_config.database_name
            collection_name=self.data_ingestion_config.collection_name
            self.mongo_client=pymongo.MongoClient(MONGO_DB_URL)
            collection=self.mongo_client[database_name][collection_name]

            df=pd.DataFrame(list(collection.find()))

            ## Drop the _id column, it comes from the MongoDB as a primary key
            if "_id" in df.columns.to_list():
                df.drop(columns=["_id"], axis=1)

            df.replace({"na":np.nan}, inplace=True)
            return df

        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def export_data_into_feature_store(self, dataframe:pd.DataFrame):

        """
            Export the dataframe into the feature store
        """
        try:
            feature_store_file_path=self.data_ingestion_config.feature_store_file_path

            dir_path=os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path, exist_ok=True)
            dataframe.to_csv(feature_store_file_path, index=False)
            return dataframe
        
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def split_data_into_train_test(self, dataframe:pd.DataFrame):
        

        try:
            train_set, test_set = train_test_split(dataframe, 
                                                   test_size=self.data_ingestion_config.train_test_split_ratio 
                                                   )
            logging.info(f"Performed the train test split with the ratio of {self.data_ingestion_config.train_test_split_ratio}")

            logging.info(f"Exited the split_data_into_train_test method")

            dir_path=os.path.dirname(self.data_ingestion_config.training_file_path)

            os.makedirs(dir_path, exist_ok=True)

            logging.info(f"Created the directory {dir_path}")

            train_set.to_csv(self.data_ingestion_config.training_file_path, index=False, header=True)

            test_set.to_csv(self.data_ingestion_config.testing_file_path, index=False, header=True)
        
            logging.info(f"Exported the train and test data into the directory {dir_path}")
        except Exception as e:
            raise NetworkSecurityException(e, sys)
   
    def initiate_data_ingestion(self):
        try:
            ## Export the collection as a dataframe
            dataframe=self.export_collection_as_dataframe()
            ## Export the dataframe into the feature store
            dataframe=self.export_data_into_feature_store(dataframe)
            ## Split the data into train and test
            self.split_data_into_train_test(dataframe) 

            # Output of the data ingestion should be the training and testing file path
            dataingestionartifact=DataIngestionArtifact(
                trained_file_path=self.data_ingestion_config.training_file_path,
                testing_file_path=self.data_ingestion_config.testing_file_path
            )

            return dataingestionartifact
        
        except Exception as e:
            raise NetworkSecurityException(e, sys)