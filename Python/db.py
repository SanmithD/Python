from pymongo import MongoClient
import os

MONGO_URL = os.getenv("MONGO_URI")

print(MONGO_URL)

mongo = MongoClient(MONGO_URL)
db = mongo["shop"]
orders = db["orders"]