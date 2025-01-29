import sys
import os 
import numpy as np 
import pandas as pd


from networksecurity.constant.training_pipeline import TARGET_COLUMN, DATA_TRANSFORMATION_IMPUTER_PARAMS
from networksecurity.entity.artifact_entity import (
    DataTransformationArtifact,
    ModelTrainerArtifact
)

from networksecurity.entity.config_entity import ModelTrainerConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.utils.main_utils.utils import save_numpy_array_data, save_object, load_object, load_numpy_array_data, evaluate_models
from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score

from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression

import mlflow
import dagshub

# Creates the mlruns in the cloud.
dagshub.init(repo_owner='PG-9-9', repo_name='NetSec', mlflow=True)


class ModelTrainer:
    def __init__(self, model_trainer_config:ModelTrainerConfig,data_transformation_artifact:DataTransformationArtifact):
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
        
        except Exception as e:
            raise NetworkSecurityException(e,sys)

    def track_mlflow(self,best_model,classification_metric):
        with mlflow.start_run():
            f1_score=classification_metric.f1_score
            precision_score=classification_metric.precision_score
            recall_score=classification_metric.recall_score

            mlflow.log_metric("F1 Score",f1_score)
            mlflow.log_metric("Precision Score",precision_score)
            mlflow.log_metric("Recall Score",recall_score)
            mlflow.sklearn.log_model(best_model,"Model")

    def train_model(self,x_train,y_train,x_test,y_test):
        models={
            "Random Forest":RandomForestClassifier(verbose=1),
            # "Decision Tree":DecisionTreeClassifier(),
            # "AdaBoost":AdaBoostClassifier(),
            # "Gradient Boosting":GradientBoostingClassifier(verbose=1),
            # "Logistic Regression":LogisticRegression(verbose=1),
        }
        params={
        
        "Decision Tree": {
            'criterion':['gini', 'entropy', 'log_loss'],
        },
        "Random Forest":{
            'n_estimators': [8,16,32,128,256]
        },
        "Gradient Boosting":{
            'learning_rate':[.1,.01,.05,.001],
            'subsample':[0.6,0.7,0.75,0.85,0.9],
            'n_estimators': [8,16,32,64,128,256]
        },
        "Logistic Regression":{},
        "AdaBoost":{
            'learning_rate':[.1,.01,.001],
            'n_estimators': [8,16,32,64,128,256]
        }
        
        }  
        model_report:dict=evaluate_models(X_train=x_train,
                                    y_train=y_train,
                                    X_test=x_test,
                                    y_test=y_test,models=models,
                                    param=params)
        
        # Get the best model from the dictionary
        best_model_score=max(sorted(model_report.values()))

        best_model_name=list(model_report.keys())[
            list(model_report.values()).index(best_model_score)
        ]

        best_model=models[best_model_name]

        # Get the classification score for the train data
        y_train_pred=best_model.predict(x_train)
        classification_train_metric=get_classification_score(y_true=y_train,y_pred=y_train_pred)

        # Get the classification score for the test data
        y_test_pred=best_model.predict(x_test)
        classification_test_metric=get_classification_score(y_true=y_test,y_pred=y_test_pred)

        ## Track the model  experiments with MLFLOW
        self.track_mlflow(best_model, classification_train_metric)
        self.track_mlflow(best_model, classification_test_metric)

        # Get the preprocessor object for transforming the data
        preprocessor=load_object(self.data_transformation_artifact.transformed_object_file_path)

        # Save the model to the model directory
        model_dir_path=os.path.dirname(self.model_trainer_config.trained_model_file_path)
        os.makedirs(model_dir_path,exist_ok=True)
        
        # Save the preprocessor object, model for predicting the data
        Network_Model=NetworkModel(preprocessor=preprocessor,model=best_model)

        # Save the model
        save_object(self.model_trainer_config.trained_model_file_path,Network_Model)

        # Model Trainer Artifact
        model_trainer_artifact=ModelTrainerArtifact(
            trained_model_file_path=self.model_trainer_config.trained_model_file_path,
            train_metric_artifact=classification_train_metric,
            test_metric_artifact=classification_test_metric
        )

        logging.info("Model Training Completed Successfully")

        return model_trainer_artifact

    def initiate_model_trainer(self)->ModelTrainerArtifact:
        try:
            logging.info("Initiating Model Training")
            
            train_file_path=self.data_transformation_artifact.transformed_train_file_path
            test_file_path=self.data_transformation_artifact.transformed_test_file_path

            logging.info("Loading Data")
            train_arr=load_numpy_array_data(train_file_path)
            test_arr=load_numpy_array_data(test_file_path)

            x_train,y_train,x_test,y_test=(train_arr[:,:-1],train_arr[:,-1],test_arr[:,:-1],test_arr[:,-1])

            model_trainer_artifact=self.train_model(x_train,y_train,x_test,y_test)

            return model_trainer_artifact
            
        except Exception as e:
            raise NetworkSecurityException(e,sys)