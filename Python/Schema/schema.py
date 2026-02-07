order_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["userId", "title", "amount", "status"],
        "properties": {
            "userId": {
                "bsonType": "string",
                "description": "User Id must be a string"
            },
            "title": {
                "bsonType": "string",
                "description": "Title must be a string"
            },
            "status": {
                "bsonType": "string",
                "description": "Status must be a string"
            },
            "amount": {
                "bsonType": "int",
                "description": "Amount must be a number"
            },
        }
    }
}