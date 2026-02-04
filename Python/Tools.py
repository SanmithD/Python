from db import orders
import time

def get_current_time():
    return {"time": time.time()}

def check_water_safety():
    return {
        "is_dangerous": True,
        "reason": "Can cause drowning or intoxication"
    }

def get_user_orders(user_id: str):
    data = list(
        orders.find(
            { "userId": user_id },
            { "_id": 0 }
        )
    )

    return data

async def run_tool(tool, input_val):
    if tool == "get_user_orders":
        return get_user_orders(input_val)
    
    return { "message": "No tool found" }