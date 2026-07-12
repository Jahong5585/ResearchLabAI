from datetime import datetime


def log(agent: str, message: str):
    time = datetime.now().strftime("%H:%M:%S")
    print(f"[{time}] [{agent}] {message}")