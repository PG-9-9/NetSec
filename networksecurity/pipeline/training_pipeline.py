import os 
import sys

from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.components.model_trainer import ModelTrainer

from networksecurity.entity.config_entity import TrainingPipelineConfig, DataIngestionConfig, DataValidationConfig, DataTransformationConfig, ModelTrainerConfig
from networksecurity.entity.artifact_entity import (
    DataTransformationArtifact,
    ModelTrainerArtifact,
    DataValidationArtifact,
    DataIngestionArtifact
)

from networksecurity.cloud.s3_syncer import S3Sync
from networksecurity.constant.training_pipeline import TRAINING_BUCKET_NAME
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging


class TrainingPipeline:
    """
    Class for managing the entire training pipeline, including data ingestion, validation, transformation, 
    model training, and synchronization of artifacts and models with an S3 bucket.

    Methods
    -------
    start_data_ingestion():
        Starts the data ingestion process.
    
    start_data_validation(data_ingestion_artifact: DataIngestionArtifact):
        Starts the data validation process.
    
    start_data_transformation(data_validation_artifact: DataValidationArtifact):
        Starts the data transformation process.
    
    start_model_trainer(data_transformation_artifact: DataTransformationArtifact) -> ModelTrainerArtifact:
        Starts the model training process.
    
    sync_artifact_dir_to_s3():
        Synchronizes the artifact directory to an S3 bucket.
    
    sync_saved_model_dir_to_s3():
        Synchronizes the saved model directory to an S3 bucket.
    
    run_pipeline():
        Runs the entire pipeline, including ingestion, validation, transformation, training, and synchronization.
    """
    def __init__(self):
        """
    Initializes the training pipeline with the necessary configurations and S3 sync objects.
        """
        self.training_pipeline_config=TrainingPipelineConfig()
        self.s3_sync=S3Sync()

    def start_data_ingestion(self):
        """
    Starts the data ingestion process by creating a DataIngestionConfig object,
    initializing the DataIngestion class, and performing the ingestion.

    Returns
    -------
    DataIngestionArtifact
        The artifact containing file paths to the ingested data.

    Raises
    ------
    NetworkSecurityException
        If an error occurs during data ingestion.
        """
        try:
            self.data_ingestion_config=DataIngestionConfig(training_pipeline_config=self.training_pipeline_config)
            logging.info("Start data Ingestion")
            data_ingestion=DataIngestion(data_ingestion_config=self.data_ingestion_config)
            data_ingestion_artifact=data_ingestion.initiate_data_ingestion()
            logging.info(f"Data Ingestion completed and artifact: {data_ingestion_artifact}")
            return data_ingestion_artifact
        
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def start_data_validation(self,data_ingestion_artifact:DataIngestionArtifact):
        """
    Starts the data validation process by creating a DataValidationConfig object,
    initializing the DataValidation class, and performing the validation.

    Parameters
    ----------
    data_ingestion_artifact : DataIngestionArtifact
        The artifact containing file paths to the ingested data.

    Returns
    -------
    DataValidationArtifact
        The artifact containing file paths to the validated data.

    Raises
    ------
    NetworkSecurityException
        If an error occurs during data validation.
        """
        try:
            data_validation_config=DataValidationConfig(training_pipeline_config=self.training_pipeline_config)
            data_validation=DataValidation(data_ingestion_artifact=data_ingestion_artifact,data_validation_config=data_validation_config)
            logging.info("Initiate the data Validation")
            data_validation_artifact=data_validation.initiate_data_validation()
            return data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def start_data_transformation(self,data_validation_artifact:DataValidationArtifact):
        """
    Starts the data transformation process by creating a DataTransformationConfig object,
    initializing the DataTransformation class, and performing the transformation.

    Parameters
    ----------
    data_validation_artifact : DataValidationArtifact
        The artifact containing file paths to the validated data.

    Returns
    -------
    DataTransformationArtifact
        The artifact containing file paths to the transformed data.

    Raises
    ------
    NetworkSecurityException
        If an error occurs during data transformation.
        """
        try:
            data_transformation_config = DataTransformationConfig(training_pipeline_config=self.training_pipeline_config)
            data_transformation = DataTransformation(data_validation_artifact=data_validation_artifact,
            data_transformation_config=data_transformation_config)
            
            data_transformation_artifact = data_transformation.initiate_data_transformation()
            return data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def start_model_trainer(self,data_transformation_artifact:DataTransformationArtifact)->ModelTrainerArtifact:
        """
    Starts the model training process by creating a ModelTrainerConfig object,
    initializing the ModelTrainer class, and performing model training.

    Parameters
    ----------
    data_transformation_artifact : DataTransformationArtifact
        The artifact containing file paths to the transformed data.

    Returns
    -------
    ModelTrainerArtifact
        The artifact containing the trained model and evaluation metrics.

    Raises
    ------
    NetworkSecurityException
        If an error occurs during model training.
        """
        try:
            self.model_trainer_config: ModelTrainerConfig = ModelTrainerConfig(
                training_pipeline_config=self.training_pipeline_config
            )

            model_trainer = ModelTrainer(
                data_transformation_artifact=data_transformation_artifact,
                model_trainer_config=self.model_trainer_config,
            )

            model_trainer_artifact = model_trainer.initiate_model_trainer()

            return model_trainer_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    ## local artifact is going to s3 bucket using AWS CLI 
    def sync_artifact_dir_to_s3(self):
        """
    Synchronizes the local artifact directory to an S3 bucket using the S3Sync class.

    Raises
    ------
    NetworkSecurityException
        If an error occurs while synchronizing the artifact directory.
        """
        try:
            aws_bucket_url = f"s3://{TRAINING_BUCKET_NAME}/artifact/{self.training_pipeline_config.timestamp}"
            self.s3_sync.sync_folder_to_s3(folder = self.training_pipeline_config.artifact_dir,aws_bucket_url=aws_bucket_url)
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    ## local final model is going to s3 bucket 
        
    def sync_saved_model_dir_to_s3(self):
        """
    Synchronizes the local saved model directory to an S3 bucket using the S3Sync class.

    Raises
    ------
    NetworkSecurityException
        If an error occurs while synchronizing the saved model directory.
        """
        try:
            aws_bucket_url = f"s3://{TRAINING_BUCKET_NAME}/final_model/{self.training_pipeline_config.timestamp}"
            self.s3_sync.sync_folder_to_s3(folder = self.training_pipeline_config.model_dir,aws_bucket_url=aws_bucket_url)
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def run_pipeline(self):
        """
    Runs the entire training pipeline, including data ingestion, validation, transformation, 
    model training, and synchronization of artifacts and models with an S3 bucket.

    Returns
    -------
    ModelTrainerArtifact
        The artifact containing the trained model and evaluation metrics.

    Raises
    ------
    NetworkSecurityException
        If any error occurs during the pipeline execution.
        """
        try:
            data_ingestion_artifact=self.start_data_ingestion()
            data_validation_artifact=self.start_data_validation(data_ingestion_artifact=data_ingestion_artifact)
            data_transformation_artifact=self.start_data_transformation(data_validation_artifact=data_validation_artifact)
            model_trainer_artifact=self.start_model_trainer(data_transformation_artifact=data_transformation_artifact)
            
            ## Sync the artifact and model to s3 bucket
            self.sync_artifact_dir_to_s3()
            self.sync_saved_model_dir_to_s3()

            return model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)
