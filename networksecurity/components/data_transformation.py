import sys
import os 
import numpy as np 
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from networksecurity.constant.training_pipeline import TARGET_COLUMN, DATA_TRANSFORMATION_IMPUTER_PARAMS
from networksecurity.entity.artifact_entity import (
    DataTransformationArtifact,
    DataValidationArtifact
)

from networksecurity.entity.config_entity import DataTransformationConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging


from networksecurity.utils.main_utils.utils import save_numpy_array_data,save_object

class DataTransformation:
    """
    A class to apply data transformation including handling missing data
    and scaling features.
    """
    
    def __init__(self, data_validation_artifact:DataValidationArtifact,
                      data_transformation_config:DataTransformationConfig):
        """
        Initializes the DataTransformation class with the provided artifacts and configuration.

        Parameters
        ----------
        data_validation_artifact : DataValidationArtifact
            The artifact containing validated data.
        data_transformation_config : DataTransformationConfig
            The configuration for the data transformation process.
        """
        try:
            self.data_validation_artifact : DataValidationArtifact = data_validation_artifact
            self.data_transformation_config : DataTransformationArtifact = data_transformation_config

        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    @staticmethod
    def read_data(file_path:str)->pd.DataFrame:
        """
        Reads a CSV file and returns it as a DataFrame.

        Parameters
        ----------
        file_path : str
            Path to the CSV file.

        Returns
        -------
        pd.DataFrame
            The loaded DataFrame.

        Raises
        ------
        NetworkSecurityException
            If an error occurs while reading the file.
        """
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    def get_data_transformer_object(self)->Pipeline:
        """
        Creates a data transformation pipeline for imputing missing values.

        Returns
        -------
        Pipeline
            A scikit-learn pipeline for data transformation.
        """
        logging.info("Creating the data transformation pipeline ")
        try:
            imputer:KNNImputer=KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)
            logging.info("KNNImputer object created")
            processor:Pipeline=Pipeline([('imputer',imputer)])
            return processor
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    
    def initiate_data_transformation(self)->DataTransformationArtifact:
        """
        Initiates the data transformation process on the training and test datasets.

        Returns
        -------
        DataTransformationArtifact
            An artifact containing paths to the transformed datasets and the transformation object.
        
        Raises
        ------
        NetworkSecurityException
            If an error occurs during the data transformation process.
        """
        logging.info("Initiating Data Transformation")
        try:
            logging.info("Reading the data under data transformation")
            train_df=DataTransformation.read_data(self.data_validation_artifact.valid_train_file_path)
            test_df=DataTransformation.read_data(self.data_validation_artifact.valid_test_file_path)
            
            
            if "_id" in  train_df.columns.to_list():
                train_df=train_df.drop(columns=["_id"], axis=1)

            if "_id" in  test_df.columns.to_list():
                test_df=test_df.drop(columns=["_id"], axis=1)

            ## Training dataframe
            input_feature_train_df=train_df.drop(columns=[TARGET_COLUMN],axis=1)
            target_feature_train_df=train_df[TARGET_COLUMN]
            target_feature_train_df=target_feature_train_df.replace(-1,0)

            ## Testing dataframe
            input_feature_test_df=test_df.drop(columns=[TARGET_COLUMN],axis=1)
            target_feature_test_df=test_df[TARGET_COLUMN]
            target_feature_test_df=target_feature_test_df.replace(-1,0)

            ## Data Transformation
            preprocessor=self.get_data_transformer_object()
            preprocessor_object=preprocessor.fit(input_feature_train_df)

            transformed_input_train_feature=preprocessor_object.transform(input_feature_train_df)
            transformed_input_test_feature=preprocessor_object.transform(input_feature_test_df)

            ## Save the transformed object
            train_arr = np.c_[transformed_input_train_feature, np.array(target_feature_train_df) ]
            test_arr = np.c_[ transformed_input_test_feature, np.array(target_feature_test_df) ]


            save_numpy_array_data(self.data_transformation_config.transformed_train_file_path,train_arr,)
            save_numpy_array_data(self.data_transformation_config.transformed_test_file_path,test_arr,)
            save_object(self.data_transformation_config.transformed_object_file_path,preprocessor_object,)

            save_object("final_model/preprocessor.pkl",preprocessor_object)

            # Prepare the artifact
            data_transformation_artifact=DataTransformationArtifact(
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path
                )
            
            return data_transformation_artifact
        
        except Exception as e:
            raise NetworkSecurityException(e,sys)