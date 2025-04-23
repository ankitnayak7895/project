"""This file is for connecting MongoDB with Python and logging connection status."""
import logging
import os
import ssl
from pymongo import MongoClient
from log import logging

# ✅ MongoDB Configuration
MONGO_URI = "mongodb+srv://ankitnayak7895:Ankitnodb@cluster0.62dva.mongodb.net/?retryWrites=true&w=majority"
DATABASE_NAME = "web_scrap_database"  # Change this to your desired database name
COLLECTION_NAME = "MyCollection"  # Change this to your desired collection name

def get_database():
    """Connects to MongoDB and returns the database object."""
    try:
        client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)  # Connect to MongoDB
        client.admin.command("ping")  # Check connection
        db = client[DATABASE_NAME]  # Get Database
        logging.info('Successfully connected to the database')
        print('Connected to the database!')
        
        # ✅ Create Collection if it does not exist
        if COLLECTION_NAME not in db.list_collection_names():
            db.create_collection(COLLECTION_NAME)
            logging.info(f"✅ Created Collection: {COLLECTION_NAME}")
        
        logging.info(f"✅ Successfully connected to MongoDB! Database: {DATABASE_NAME}")
        return db  # ✅ Return the database object
    
    except Exception as e:
        logging.error(f"❌ Failed to connect to MongoDB: {e}")
        return None  # Return None if connection fails

# ✅ Test connection when running directly
if __name__ == "__main__":
    db = get_database()
    
    if db is not None:
        print(f"✅ Database `{DATABASE_NAME}` is ready with collection `{COLLECTION_NAME}`.")
    else:
        print(f"✅ Database `{DATABASE_NAME}` is ready with collection `{COLLECTION_NAME}`.")
