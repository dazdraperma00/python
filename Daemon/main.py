import asyncio
from deamon import Daemon
import threading


def foo(path):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    d = Daemon(path)
    d.start()


path_a = "config/config_a.yaml"
path_b = "config/config_b.yaml"
path_c = "config/config_c.yaml"

threads = [
    threading.Thread(target=foo, args=(path_a, )),
    threading.Thread(target=foo, args=(path_b, )),
    threading.Thread(target=foo, args=(path_c, ))
]
for t in threads:
    t.start()
for t in threads:
    t.join()
