from sys import path
from pathlib import Path

current_dir = Path(__file__).resolve().parent
apps_dir = current_dir.parent.parent
path.append(str(apps_dir))


import asyncio
import uvloop

loop_police = uvloop.EventLoopPolicy()
asyncio.set_event_loop_policy(loop_police)


from .app import App


App().start()
