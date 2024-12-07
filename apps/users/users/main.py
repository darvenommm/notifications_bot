from sys import path
from pathlib import Path

current_dir = Path(__file__).resolve().parent
path.append(str(current_dir.parent))


import asyncio
import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


from users.container import Container

if __name__ == "__main__":
    Container().app().start()
