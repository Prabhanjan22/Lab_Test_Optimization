from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "labopti")

class DatabaseManager:
    _instance = None
    _client: MongoClient = None
    _db: Database = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def connect(self):
        if self._client is None:
            self._client = MongoClient(MONGODB_URI)
            self._db = self._client[DATABASE_NAME]
            print(f"Connected to MongoDB: {DATABASE_NAME}")
    
    def get_collection(self, collection_name: str) -> Collection:
        if self._db is None:
            self.connect()
        return self._db[collection_name]
    
    def close(self):
        if self._client:
            self._client.close()
            print("MongoDB connection closed")

db_manager = DatabaseManager()

def get_patients_collection() -> Collection:
    return db_manager.get_collection("patients")

def find_patient(patient_id: str):
    collection = get_patients_collection()
    return collection.find_one({"patient_id": patient_id})

def insert_patient(patient_data: dict):
    collection = get_patients_collection()
    return collection.insert_one(patient_data)

def update_patient(patient_id: str, update_data: dict):
    collection = get_patients_collection()
    return collection.update_one(
        {"patient_id": patient_id},
        {"$set": update_data}
    )

def add_visit_to_patient(patient_id: str, visit_data: dict):
    collection = get_patients_collection()
    return collection.update_one(
        {"patient_id": patient_id},
        {"$push": {"visits": visit_data}}
    )

def update_visit(patient_id: str, visit_id: str, update_data: dict):
    collection = get_patients_collection()
    return collection.update_one(
        {"patient_id": patient_id, "visits.visit_id": visit_id},
        {"$set": {f"visits.$.{key}": value for key, value in update_data.items()}}
    )
