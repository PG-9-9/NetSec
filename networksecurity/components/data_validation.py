from networksecurity.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from networksecurity.entity.config_entity import DataValidationConfig, TrainingPipelineConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.constant.training_pipeline import SCHEMA_FILE_PATH
from networksecurity.utils.main_utils.utils import read_yaml_file, write_yaml_file
from scipy.stats import ks_2samp
import pandas as pd
import os 
import sys

class DataValidation:
    """
    Validates data by checking schema compliance, column existence, and performs statistical tests for data drift.
    """
    def __init__(self,data_ingestion_artifact:DataIngestionArtifact, 
                 data_validation_config:DataValidationConfig):
        """
    Initializes the DataValidation class with the provided artifacts and configuration.

    Parameters
    ----------
    data_ingestion_artifact : DataIngestionArtifact
        Artifact containing the ingested data.
    data_validation_config : DataValidationConfig
        Configuration for the data validation process.
        """
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self.schema_config=read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    # No need to create a object, so make it static
    @staticmethod
    def read_data(file_path:str)->pd.DataFrame:
        """
    Reads a CSV file and returns it as a pandas DataFrame.

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
    
    def validate_number_of_columns(self,dataframe:pd.DataFrame)->bool:
        """
    Validates the number of columns in the provided dataframe against the expected schema.

    Parameters
    ----------
    dataframe : pd.DataFrame
        The DataFrame to be validated.

    Returns
    -------
    bool
        True if the number of columns is correct, otherwise False.
    """
        try:
            number_of_columns=len(self.schema_config)#
            logging.info(f"Required Number of columns: {number_of_columns}")
            logging.info(f"Actual Number of columns: {len(dataframe.columns)}")
            if number_of_columns==len(dataframe.columns):
                return True
            else:
                return False
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def numerical_columns_exists(self, dataframe: pd.DataFrame) -> bool:
        """
    Checks if all numerical columns specified in the schema exist in the provided DataFrame.

    Parameters
    ----------
    dataframe : pd.DataFrame
        The DataFrame to check for numerical columns.

    Returns
    -------
    bool
        True if the numerical columns exist, otherwise False.
    """
        try:
            # Check if 'columns' and 'numerical_columns' exist in the schema
            if 'columns' not in self.schema_config or 'numerical_columns' not in self.schema_config:
                raise ValueError("Schema configuration missing 'columns' or 'numerical_columns'")

            # Extract column names (keys) from the dictionaries in 'columns' list
            total_column_names = {list(col.keys())[0] for col in self.schema_config['columns']}
            
            # Extract numerical column names from the list 'numerical_columns'
            numerical_columns = {col for col in self.schema_config['numerical_columns']}

            # Check if the numerical_columns are a subset of total_column_names
            if numerical_columns.issubset(total_column_names):
                return True
            else:
                return False
        except Exception as e:
            raise NetworkSecurityException(e, sys)


    def detect_dataset_drift(self,base_df, current_df, threshold=0.05)->bool:
        """
    Detects data drift between the base and current datasets by comparing distributions.

    Parameters
    ----------
    base_df : pd.DataFrame
        The baseline dataset to compare against.
    current_df : pd.DataFrame
        The current dataset to be compared.
    threshold : float, optional
        The p-value threshold to determine if drift is present (default is 0.05).

    Returns
    -------
    bool
        True if drift is detected, otherwise False.

    Saves the drift report to the configured file path.
    """
        try:
            status=True
            report={}
            for column in base_df.columns:
                d1=base_df[column]
                d2=current_df[column]
                is_same_dist=ks_2samp(d1,d2)
                # If the p-value is less than the threshold, the distributions are different
                if threshold<is_same_dist.pvalue:
                    is_found=False
                else:
                    is_found=True
                    status=False
                report.update({column:
                               {
                                   "p_value":float(is_same_dist.pvalue),
                                   "drift_status":is_found
                               }})
            drift_report_file_path=self.data_validation_config.drift_report_file_path
            dir_path=os.path.dirname(drift_report_file_path)
            os.makedirs(dir_path,exist_ok=True)
            write_yaml_file(file_path=drift_report_file_path,content=report)

        except Exception as e:
            raise NetworkSecurityException(e,sys)

    def initiate_data_validation(self)->DataValidationArtifact:
        """
    Initiates the data validation process, validating the number of columns, numerical columns, and detecting drift.

    Returns
    -------
    DataValidationArtifact
        An artifact containing validation status and file paths to the validated data.
    
    Raises
    ------
    NetworkSecurityException
        If any validation checks fail.
    """
        try:
            train_file_path=self.data_ingestion_artifact.trained_file_path
            test_file_path=self.data_ingestion_artifact.testing_file_path

            # Read the data
            train_dataframe=DataValidation.read_data(train_file_path)
            test_dataframe=DataValidation.read_data(test_file_path)

            # Validate the number of columns
            status=self.validate_number_of_columns(train_dataframe)
            if not status:
                error_message=f"Train number of columns are not matching"
            status=self.validate_number_of_columns(test_dataframe)
            if not status:
                error_message=f"Test number of columns are not matching"

            # Validate the numerical columns
            status=self.numerical_columns_exists(train_dataframe)
            if not status:
                error_message=f"Train numerical columns are not matching"
            status=self.numerical_columns_exists(test_dataframe)
            if not status:
                error_message=f"Test numerical columns are not matching"

            # Data Drift 
            self.detect_dataset_drift(base_df=train_dataframe,current_df=test_dataframe)
            dir_path=os.path.dirname(self.data_validation_config.valid_train_file_path)
            os.makedirs(dir_path,exist_ok=True)

            train_dataframe.to_csv(self.data_validation_config.valid_train_file_path,index=False, header=True)
            test_dataframe.to_csv(self.data_validation_config.valid_test_file_path,index=False, header=True)        
        
            data_validation_artifact=DataValidationArtifact(
                validation_status=status,
                valid_train_file_path=self.data_ingestion_artifact.trained_file_path,
                valid_test_file_path=self.data_ingestion_artifact.testing_file_path,
                invalid_train_file_path=None,
                invalid_test_file_path=None,
                drift_report_file_path=self.data_validation_config.drift_report_file_path
             )
            
            return data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)