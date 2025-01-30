from datetime import datetime
import os
from networksecurity.constant import training_pipeline

print(training_pipeline.PIEPELINE_NAME)
print(training_pipeline.ARTIFACT_DIR)

class TrainingPipelineConfig:
    """
    Configuration for the training pipeline, including paths and artifact directories.

    Attributes
    ----------
    pipeline_name : str
        Name of the pipeline.
    artifact_name : str
        Name of the artifact directory.
    artifact_dir : str
        Path to the directory where pipeline artifacts will be stored.
    model_dir : str
        Path to the final model directory.
    timestamp : str
        Timestamp used for versioning the artifact directory.

    Methods
    -------
    __init__(self, timestamp=datetime.now()):
        Initializes the training pipeline configuration.
    """
    def __init__(self,timestamp=datetime.now()):
        """
    Initializes the training pipeline configuration with the provided timestamp.

    Parameters
    ----------
    timestamp : datetime
        The timestamp for the current pipeline run, formatted as "%m_%d_%Y_%H_%M_%S".
        """
        timestamp = timestamp.strftime("%m_%d_%Y_%H_%M_%S")
        self.pipeline_name = training_pipeline.PIEPELINE_NAME
        self.artifact_name = training_pipeline.ARTIFACT_DIR
        self.artifact_dir = os.path.join(self.artifact_name, timestamp)
        self.model_dir=os.path.join("final_model")
        self.timestamp :str = timestamp
        
class DataIngestionConfig:
    """
    Configuration for data ingestion, including paths for feature store, training, and test data.

    Attributes
    ----------
    data_ingestion_dir : str
        Path to the directory where data ingestion artifacts will be stored.
    feature_store_file_path : str
        Path to the feature store file.
    training_file_path : str
        Path to the training dataset file.
    testing_file_path : str
        Path to the testing dataset file.
    train_test_split_ratio : float
        Ratio of train-test split for the dataset.
    collection_name : str
        The MongoDB collection name to ingest data from.
    database_name : str
        The MongoDB database name to ingest data from.

    Methods
    -------
    __init__(self, training_pipeline_config: TrainingPipelineConfig):
        Initializes the data ingestion configuration with the provided pipeline configuration.
    """
    def __init__(self, training_pipeline_config:TrainingPipelineConfig):
        """
    Initializes the data ingestion configuration with the provided training pipeline configuration.

    Parameters
    ----------
    training_pipeline_config : TrainingPipelineConfig
        The training pipeline configuration object containing directory paths and names.
        """
        self.data_ingestion_dir:str=os.path.join(
            training_pipeline_config.artifact_dir,
            training_pipeline.DATA_INGESTION_DIR_NAME
        )
        self.feature_store_file_path:str=os.path.join(
            self.data_ingestion_dir,
            training_pipeline.DATA_INGESTION_FEATURE_STORE_DIR
        )
        self.training_file_path:str=os.path.join(
            self.data_ingestion_dir,
            training_pipeline.TRAIN_FILE_NAME
        )
        self.testing_file_path:str=os.path.join(
            self.data_ingestion_dir,
            training_pipeline.TEST_FILE_NAME
        )
        self.train_test_split_ratio:float=training_pipeline.DATA_INGESTION_TRAIN_TEST_SPLIT_RATION
        self.collection_name:str=training_pipeline.DATA_INGESTION_COLLECTION_NAME
        self.database_name:str=training_pipeline.DATA_INGESTION_DATABASE_NAME


class DataValidationConfig:
    """
    Configuration for data validation, including paths for valid and invalid data, and drift report.

    Attributes
    ----------
    data_validation_dir : str
        Path to the directory where data validation artifacts will be stored.
    valid_data_dir : str
        Path to the directory where valid data will be stored.
    invalid_data_dir : str
        Path to the directory where invalid data will be stored.
    valid_train_file_path : str
        Path to the valid training data file.
    valid_test_file_path : str
        Path to the valid testing data file.
    invalid_train_file_path : str
        Path to the invalid training data file.
    invalid_test_file_path : str
        Path to the invalid testing data file.
    drift_report_file_path : str
        Path to the file where data drift reports will be stored.

    Methods
    -------
    __init__(self, training_pipeline_config: TrainingPipelineConfig):
        Initializes the data validation configuration with the provided pipeline configuration.
    """
    def __init__(self, training_pipeline_config:TrainingPipelineConfig):
        """
    Initializes the data validation configuration with the provided training pipeline configuration.

    Parameters
    ----------
    training_pipeline_config : TrainingPipelineConfig
        The training pipeline configuration object containing directory paths and names.
        """
        self.data_validation_dir:str=os.path.join(
            training_pipeline_config.artifact_dir,
            training_pipeline.DATA_VALIDATION_DIR_NAME
        )
        self.valid_data_dir:str=os.path.join(
            self.data_validation_dir,
            training_pipeline.DATA_VALIDATION_VALID_DIR
        )
        self.invalid_data_dir:str=os.path.join(
            self.data_validation_dir,
            training_pipeline.DATA_VALIDATION_INVALID_DIR
        )
        self.valid_train_file_path:str=os.path.join(
            self.valid_data_dir,
            training_pipeline.TRAIN_FILE_NAME
        )
        self.valid_test_file_path:str=os.path.join(
            self.valid_data_dir,
            training_pipeline.TEST_FILE_NAME
        )
        self.invalid_train_file_path:str=os.path.join(
            self.invalid_data_dir,
            training_pipeline.TRAIN_FILE_NAME
        )
        self.invalid_test_file_path:str=os.path.join(
            self.invalid_data_dir,
            training_pipeline.TEST_FILE_NAME
        )
        self.drift_report_file_path:str=os.path.join(
            self.data_validation_dir,
            training_pipeline.DATA_VALIDATION_DRIFT_REPORT_DIR,
            training_pipeline.DATA_VALIDATION_DRIFT_REPORT_FILE_NAME
        )

class DataTransformationConfig:
    """
    Configuration for data transformation, including paths for transformed data and transformation objects.

    Attributes
    ----------
    data_transformation_dir : str
        Path to the directory where data transformation artifacts will be stored.
    transformed_train_file_path : str
        Path to the transformed training data file.
    transformed_test_file_path : str
        Path to the transformed testing data file.
    transformed_object_file_path : str
        Path to the preprocessor transformation object.

    Methods
    -------
    __init__(self, training_pipeline_config: TrainingPipelineConfig):
        Initializes the data transformation configuration with the provided pipeline configuration.
    """     
    def __init__(self,training_pipeline_config:TrainingPipelineConfig):
        """
    Initializes the data transformation configuration with the provided training pipeline configuration.

    Parameters
    ----------
    training_pipeline_config : TrainingPipelineConfig
        The training pipeline configuration object containing directory paths and names.
        """
        self.data_transformation_dir: str = os.path.join( training_pipeline_config.artifact_dir,training_pipeline.DATA_TRANSFORMATION_DIR_NAME )
        self.transformed_train_file_path: str = os.path.join( self.data_transformation_dir,training_pipeline.DATA_TRANSFORMATION_TRANSFORMED_DATA_DIR,
            training_pipeline.TRAIN_FILE_NAME.replace("csv", "npy"),)
        self.transformed_test_file_path: str = os.path.join(self.data_transformation_dir,  training_pipeline.DATA_TRANSFORMATION_TRANSFORMED_DATA_DIR,
            training_pipeline.TEST_FILE_NAME.replace("csv", "npy"), )
        self.transformed_object_file_path: str = os.path.join( self.data_transformation_dir, training_pipeline.DATA_TRANSFORMATION_TRANSFORMED_OBJECT_DIR,
            training_pipeline.PREPROCESSING_OBJECT_FILE_NAME,)
        
class ModelTrainerConfig:
    """
    Configuration for model training, including paths for the trained model and expected accuracy.

    Attributes
    ----------
    model_trainer_dir : str
        Path to the directory where model training artifacts will be stored.
    trained_model_file_path : str
        Path to the trained model file.
    expected_accuracy : float
        The expected accuracy score for the trained model.
    overfitting_underfitting_threshold : float
        The threshold for determining overfitting or underfitting.

    Methods
    -------
    __init__(self, training_pipeline_config: TrainingPipelineConfig):
        Initializes the model trainer configuration with the provided pipeline configuration.
    """
    def __init__(self,training_pipeline_config:TrainingPipelineConfig):
        """
    Initializes the model trainer configuration with the provided training pipeline configuration.

    Parameters
    ----------
    training_pipeline_config : TrainingPipelineConfig
        The training pipeline configuration object containing directory paths and names.
        """
        self.model_trainer_dir: str = os.path.join(
            training_pipeline_config.artifact_dir, training_pipeline.MODEL_TRAINER_DIR_NAME
        )
        self.trained_model_file_path: str = os.path.join(
            self.model_trainer_dir, training_pipeline.MODEL_TRAINER_TRAINED_MODEL_DIR, 
            training_pipeline.MODEL_FILE_NAME
        )
        self.expected_accuracy: float = training_pipeline.MODEL_TRAINER_EXPECTED_SCORE
        self.overfitting_underfitting_threshold = training_pipeline.MODEL_TRAINER_OVER_FIITING_UNDER_FITTING_THRESHOLD
        