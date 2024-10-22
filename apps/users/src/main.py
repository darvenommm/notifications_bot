from sys import path
from pathlib import Path

current_dir = Path(__file__).resolve().parent
path.append(str(current_dir.parent.parent))
path.append(str(current_dir.parent.parent.parent))


import asyncio
import uvloop


loop_police = uvloop.EventLoopPolicy()
asyncio.set_event_loop_policy(loop_police)


from users.src.container import Container


if __name__ == "__main__":
    container = Container()
    container.config.rabbit_connection_string.from_value(
        container.rabbit_settings().rabbit_connection_string
    )
    container.app().start()
