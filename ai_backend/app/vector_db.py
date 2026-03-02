import os
from pymongo import MongoClient

MONGO_URL = os.getenv("MONGO_URI")

client = MongoClient("mongodb+srv://sanmithdevadiga91_db_user:YMgOxzvnFlq3Zq68@cluster0.ikxh0hk.mongodb.net/")
db = client["ai_backend"]
collection = db["docs"]
print(client.list_database_names())