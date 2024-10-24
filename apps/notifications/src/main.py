from pathlib import Path
from sys import path


current_dir = Path(__file__).resolve().parent
path.append(str(current_dir.parent.parent))
path.append(str(current_dir.parent.parent.parent))


import asyncio
import uvloop


if uvloop is not None:
    loop_policy = uvloop.EventLoopPolicy()
    asyncio.set_event_loop_policy(loop_policy)


from notifications.src.container import Container


if __name__ == "__main__":
    container = Container()
    container.config.rabbit_connection_string.from_value(
        container.rabbit_settings().rabbit_connection_string
    )

    container.app().start()
