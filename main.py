from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.components.model_trainer import ModelTrainer
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.config_entity import DataIngestionConfig, DataValidationConfig, DataTransformationConfig, ModelTrainerConfig
from networksecurity.entity.config_entity import TrainingPipelineConfig
from datetime import datetime



import sys

if __name__=="__main__":
    """
    Main entry point for running the training pipeline components sequentially.
    
    It handles the entire pipeline starting from data ingestion to model training, 
    logging the progress, and printing the artifacts at each stage.
    
    Methods
    -------
    start_data_ingestion():
        Starts data ingestion and returns the data ingestion artifact.
    
    start_data_validation():
        Starts data validation and returns the data validation artifact.
    
    start_data_transformation():
        Starts data transformation and returns the data transformation artifact.
    
    start_model_trainer():
        Starts model training and returns the model trainer artifact.
    """
    try:
        trainingpipelineconfig=TrainingPipelineConfig()
        dataingestionconfig=DataIngestionConfig(trainingpipelineconfig)
        data_ingestion=DataIngestion(dataingestionconfig)
        logging.info("Data Ingestion object created")
        dataingestionartifact=data_ingestion.initiate_data_ingestion()
        logging.info("Data Ingestion completed")
        print(dataingestionartifact)

        data_validation_config=DataValidationConfig(trainingpipelineconfig)
        data_validation=DataValidation(dataingestionartifact,data_validation_config)
        logging.info("Data Validation object created")
        data_validation_artifact=data_validation.initiate_data_validation()
        print(data_validation_artifact)
        logging.info("Data Validation completed")

        data_transformation_config=DataTransformationConfig(trainingpipelineconfig)
        data_transformation=DataTransformation(data_validation_artifact,data_transformation_config)
        logging.info("Data Transformation object created")
        data_transformation_artifact=data_transformation.initiate_data_transformation()
        print(data_transformation_artifact)
        logging.info("Data Transformation completed")

        model_trainer_config=ModelTrainerConfig(trainingpipelineconfig)
        model_trainer=ModelTrainer(model_trainer_config=model_trainer_config,data_transformation_artifact=data_transformation_artifact)
        logging.info("Model Trainer object created")
        model_trainer_artifact=model_trainer.initiate_model_trainer()
        print(model_trainer_artifact)
        logging.info("Model Training completed")

    except Exception as e:
            raise NetworkSecurityException(e, sys) # sys is passed as the error_details argument