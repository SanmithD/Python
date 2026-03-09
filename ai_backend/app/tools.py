def getCurrentDate(_=None):
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def calculateExpr(expression: str):
    try:
        return str(eval(expression))
    except:
        return "Invalid Expression"