from pymongo import MongoClient
import os
from Schema.schema import order_schema
from TypeSafety import InputOrder

MONGO_URL = os.getenv("MONGO_URI")

print(MONGO_URL)

mongo = MongoClient(MONGO_URL)
db = mongo["shop"]
orders = db["orders"]

collection_name = "orders"

try:
    if __name__ == "__main__":
        db.create_collection(collection_name, validator=order_schema)
        print('Connected to', collection_name)
except Exception as e:
    print("Error", e)

def insertDoc(input: InputOrder) -> str:
    print("Input", input.model_dump())
    db[collection_name].insert_one(input.model_dump())

    return "Data Inserted"