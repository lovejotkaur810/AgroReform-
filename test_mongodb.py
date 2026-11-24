from pymongo import MongoClient
from config import MONGO_URI

try:
    client = MongoClient(MONGO_URI)

    # Test the connection
    client.admin.command("ping")

    print("===================================")
    print("MongoDB connection successful!")
    print("AgroReForm database is reachable.")
    print("===================================")

except Exception as e:
    print("===================================")
    print("MongoDB connection failed!")
    print("Error:", e)
    print("===================================")