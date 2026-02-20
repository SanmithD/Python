def small_greet(message: str):

    small_talk = [
        "hi",
        "hello",
        "hey",
        "i am",
        "im ",
        "who are you",
        "how are you"
    ]

    message = message.lower()

    return any(keyword in message for keyword in small_talk)

def is_tech_message(msg: str):

    keywords = ["api", "database", "fastapi", "rag", "vector", "ai"]
    msg = msg.lower()

    return any(word in msg for word in keywords)