import sys, os
from dotenv import load_dotenv
import certifi
import pymongo
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.pipeline.training_pipeline import TrainingPipeline
from networksecurity.utils.main_utils.utils import load_object
from networksecurity.constant.training_pipeline import DATA_INGESTION_COLLECTION_NAME, DATA_INGESTION_DATABASE_NAME

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile,Request
from uvicorn import run as app_run
from fastapi.responses import Response
from starlette.responses import RedirectResponse
import pandas as pd

# Get the path of the certificate file
ca=certifi.where()

# Load the environment variables
load_dotenv()
## TODO: Check the environment variables
mongo_db_url=os.getenv("MONGO_DB_URL")
print(mongo_db_url)

# Create a connection to the MongoDB database
client=pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)
database=client[DATA_INGESTION_DATABASE_NAME]
collection=database[DATA_INGESTION_COLLECTION_NAME]

# Create a FastAPI instance
app=FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Generic API home page
@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")

# API to train the model
@app.get("/train")
async def train_route():
    try:
        train_pipeline=TrainingPipeline()
        train_pipeline.run_pipeline()
        return Response('Training Pipeline Completed Successfully')
    except Exception as e:
        raise NetworkSecurityException(e, sys)
    
if __name__ == "__main__":
    # Run the FastAPI application
    app_run(app, host="localhost", port=8000)