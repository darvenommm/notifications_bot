from pathlib import Path
from sys import path

current_dir = Path(__file__).resolve().parent
path.append(str(current_dir.parent))


import asyncio

import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


from notifications.container import Container

if __name__ == "__main__":
    Container().app().start()
